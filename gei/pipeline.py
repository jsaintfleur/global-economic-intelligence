from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .adapters import SourceAdapter, WorldBankAdapter
from .config import APP_DATA, DIFFS, END_YEAR, MANIFESTS, PROCESSED, RAW, REGRESSION_RULES_PATH, RELEASES, ROOT, START_YEAR, TOP_N, load_metric_registry
from .analytics import country_profile, ranking_asset
from .coverage import coverage_matrix
from .capabilities import metric_capabilities
from .diff import snapshot_diff, write_diff
from .ids import stable_id
from .manifest import PipelineManifest
from .logging import log_event
from .registries import ANALYTICAL_ENTITY_REGISTRY_PATH, COUNTRY_REGISTRY_PATH, SOURCE_REGISTRY_PATH, TRANSFORMATION_REGISTRY_PATH, load_versioned_registry, registry_version, validate_analytical_entity_registry, validate_country_registry, validate_registries, write_country_registry
from .regression import evaluate_regressions
from .release import build_release, write_release
from .weo import read_metric_fixture_observations, read_ngdpd_snapshot, select_weo_universe
from .validation import validate_metric_registry, validate_observations


def build(start: int = START_YEAR, end: int = END_YEAR, adapter: SourceAdapter | None = None, now: str | None = None) -> dict:
    started_at = now or datetime.now(timezone.utc).isoformat()
    run_id = stable_id("run", started_at, start, end)
    metrics = load_metric_registry()
    validate_metric_registry(metrics).require_valid()
    sources = load_versioned_registry(SOURCE_REGISTRY_PATH, "sources")["sources"]
    transformations = load_versioned_registry(TRANSFORMATION_REGISTRY_PATH, "transformations")["transformations"]
    entity_registry = load_versioned_registry(ANALYTICAL_ENTITY_REGISTRY_PATH, "entities")
    entity_errors = validate_analytical_entity_registry(entity_registry)
    if entity_errors: raise ValueError("Analytical entity registry validation failed: " + "; ".join(entity_errors))
    registry_errors = validate_registries(metrics, sources, transformations)
    if registry_errors: raise ValueError("Registry validation failed: " + "; ".join(registry_errors))
    manifest = PipelineManifest(run_id, started_at, None, "running", sorted({m["source_id"] for m in metrics}), [m["source_indicator_id"] for m in metrics], "all source countries")
    log_event("pipeline_started",pipeline_run_id=run_id,stage="initialize",source_ids=manifest.source_ids)
    adapter = adapter or WorldBankAdapter(RAW)
    try:
        country_result = adapter.fetch_countries(started_at)
        manifest.raw_snapshots.append(country_result.snapshot.to_dict())
        manifest.warnings.extend(country_result.warnings)
        countries = _normalize_countries(country_result.records)
        country_registry = write_country_registry(list(countries.values()),COUNTRY_REGISTRY_PATH)
        country_errors = validate_country_registry(country_registry)
        if country_errors: raise ValueError("Country registry validation failed: " + "; ".join(country_errors))
        observations: list[dict] = []
        rejected: list[dict] = []
        for definition in (metric for metric in metrics if metric["source_id"] == adapter.source_id):
            result = adapter.fetch_indicator(definition["source_indicator_id"], start, end, started_at)
            manifest.raw_snapshots.append(result.snapshot.to_dict())
            manifest.warnings.extend(result.warnings)
            manifest.raw_observations_received += len(result.records)
            normalized, discarded = _normalize_observations(result.records, definition, countries, result.snapshot.raw_snapshot_id, run_id, started_at)
            observations.extend(normalized); rejected.extend(discarded)
        governance = ROOT / "governance"
        entity_evidence = governance / "entities"
        universe_data = read_ngdpd_snapshot(
            governance / "fixtures" / "weo_2026-04-14" / "ngdpd_2024_raw.csv.gz",
            entity_evidence / "imf_weo_reference_list.yaml",
            entity_evidence / "eligibility_adjudication.yaml",
        )
        universe, universe_exclusions = select_weo_universe(
            universe_data, entity_evidence / "eligibility_adjudication.yaml", TOP_N
        )
        reference_year = universe[0]["reference_year"]
        for country in universe:
            wb = countries.get(country["iso3"], {})
            country.update(
                {
                    "iso2": wb.get("iso2"),
                    "region": wb.get("region", "Not classified"),
                    "income_group": wb.get("income_group", "Not classified"),
                    "name": country["display_name"],
                    "eligibility_policy_version": entity_registry["eligibility_policy_version"],
                }
            )
        weo_observations, weo_snapshots = read_metric_fixture_observations(
            governance / "fixtures" / "weo_metrics_2026-04-14",
            entity_evidence / "imf_weo_reference_list.yaml",
            metrics,
            run_id,
            started_at,
            reference_year,
            {country["iso3"] for country in universe},
        )
        observations.extend(weo_observations)
        manifest.raw_snapshots.extend(weo_snapshots)
        manifest.raw_observations_received += len(weo_observations)
        universe_iso3 = [row["iso3"] for row in universe]
        panel = sorted((row for row in observations if row["iso3"] in universe_iso3), key=lambda row: (row["metric_id"], row["iso3"], row["year"]))
        validation = validate_observations(panel, universe, metrics)
        validation.require_valid()

        completed_at = now or datetime.now(timezone.utc).isoformat()
        used_source_ids = {metric["source_id"] for metric in metrics}
        source_registry = [{**source,"name":f"{source['organization']} — {source['dataset']}","url":source["documentation_reference"],"retrieved_at":started_at,"license":source["license_name"],"credibility":"Primary multilateral"} for source in sources if source["source_id"] in used_source_ids]
        metric_payload = [{**metric, "ranking_year":reference_year, "capabilities":metric_capabilities(metric), "name": metric["display_name"], "code": metric["source_indicator_id"], "family": metric["category"], "format": metric["formatting"], "caveats": metric["caveat"]} for metric in metrics]
        metric_ranking_years = {metric["metric_id"]: reference_year for metric in metrics}
        payload = {"meta": {"schema_version": "2.2", "pipeline_run_id": run_id, "generated_at": completed_at, "reference_year": reference_year, "universe_size": len(universe), "start_year": start, "end_year": end, "freshness_rules": {"annual":{"current_year":0,"prior_year":1,"historical_min_lag":2,"unavailable":"no_observation"}}, "eligibility_policy_version": entity_registry["eligibility_policy_version"], "universe_provider_id": "imf_weo", "candidate_universe_complete": True, "universe_exclusions": universe_exclusions, "universe_lineage": {"provider_id":"imf_weo","ranking_indicator":"NGDPD","reference_year":reference_year,"cohort_actual_coverage":"50/50","pool_actual_coverage":f"{universe_data.pool_actual_count}/{universe_data.pool_count}","selected_count":len(universe),"boundary_included":universe[-1],"boundary_excluded":universe_exclusions[0],"publication_date":universe_data.publication_date,"update_date":universe_data.update_date},"metric_ranking_years":metric_ranking_years}, "countries": universe, "metrics": metric_payload, "sources": source_registry, "observations": panel}
        previous = json.loads((PROCESSED / "dashboard.json").read_text()) if (PROCESSED / "dashboard.json").exists() else None
        registry_versions={"metric_registry":registry_version(ROOT/"config/metrics.json"),"country_registry":registry_version(COUNTRY_REGISTRY_PATH),"analytical_entity_registry":registry_version(ANALYTICAL_ENTITY_REGISTRY_PATH),"source_registry":registry_version(SOURCE_REGISTRY_PATH),"transformation_registry":registry_version(TRANSFORMATION_REGISTRY_PATH)}
        code_commit=_code_commit()
        release=build_release(payload,[row["raw_snapshot_id"] for row in manifest.raw_snapshots],code_commit,registry_versions,{adapter.source_id:"1.0","imf_weo":"9.0.0"},manifest.warnings)
        payload["meta"].update({"release_id":release["release_id"],"asset_version":release["asset_version"],"data_release_schema_version":"1.0"})
        diff=snapshot_diff(previous,payload) if previous else None
        rules=json.loads(REGRESSION_RULES_PATH.read_text())["rules"]
        regression=evaluate_regressions(previous,payload,diff,rules,{m["metric_id"] for m in metrics})
        if regression["status"]=="failed": raise ValueError("Blocking regression gate failed")
        outputs = _write_outputs(payload, panel, universe, rejected)
        coverage=coverage_matrix(panel,universe,metric_payload,start,end);coverage_bytes=json.dumps(coverage,separators=(",", ":"),sort_keys=True);(PROCESSED/"coverage.json").write_text(coverage_bytes,encoding="utf-8");(APP_DATA/"coverage.json").write_text(coverage_bytes,encoding="utf-8")
        release_path,snapshot_path=write_release(release,payload,RELEASES);outputs.extend([_display_path(release_path),_display_path(snapshot_path),"data/processed/coverage.json"])
        if diff and previous.get("meta",{}).get("release_id") and previous["meta"]["release_id"]!=release["release_id"]:
            paths=write_diff(diff,DIFFS,previous["meta"]["release_id"],release["release_id"]);outputs.extend(_display_path(path) for path in paths)
        regression_path=RELEASES/f"{release['release_id']}.regression.json";regression_path.write_text(json.dumps(regression,indent=2,sort_keys=True)+"\n",encoding="utf-8");outputs.append(_display_path(regression_path))
        manifest.completed_at = completed_at; manifest.status = "completed"
        manifest.accepted_observations = len(observations); manifest.rejected_observations = len(rejected)
        manifest.missing_observations = len(countries) * len(metrics) * (end - start + 1) - len(observations)
        manifest.output_files = outputs
        manifest_path = manifest.write(MANIFESTS)
        payload["meta"]["manifest_path"] = str(manifest_path.relative_to(MANIFESTS.parent.parent))
        _write_dashboard_json(payload)
        log_event("pipeline_completed",pipeline_run_id=run_id,stage="complete",release_id=release["release_id"],accepted_observations=len(observations),rejected_observations=len(rejected),warnings=len(manifest.warnings))
        return payload
    except Exception as exc:
        manifest.completed_at = datetime.now(timezone.utc).isoformat(); manifest.status = "failed"; manifest.errors.append(str(exc)); manifest.write(MANIFESTS);log_event("pipeline_failed",severity="error",pipeline_run_id=run_id,stage="failed",error=str(exc))
        raise


def _normalize_countries(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: {"country_id": f"country:{row['id']}", "iso2": row["iso2Code"], "iso3": row["id"], "name": row["name"], "region": row["region"]["value"], "income_group": row["incomeLevel"]["value"]} for row in rows if row.get("region", {}).get("id") not in (None, "NA") and len(row.get("id", "")) == 3}


def _normalize_observations(rows: list[dict], metric: dict, countries: dict[str, dict], snapshot_id: str, run_id: str, retrieved_at: str) -> tuple[list[dict], list[dict]]:
    accepted, rejected = [], []
    seen: set[tuple[str, int]] = set()
    for index, row in enumerate(rows):
        iso3, period, value = row.get("countryiso3code"), row.get("date"), row.get("value")
        reason = None
        if iso3 not in countries: reason = "unknown_or_aggregate_country"
        try: year = int(period)
        except (TypeError, ValueError): year = 0; reason = reason or "malformed_reference_period"
        if value is None: reason = reason or "missing_value"
        elif not isinstance(value, (int, float)): reason = reason or "nonnumeric_value"
        if (iso3, year) in seen: reason = reason or "duplicate_source_observation"
        if reason:
            rejected.append({"source_indicator_id": metric["source_indicator_id"], "raw_record_index": index, "reason": reason, "raw_country_code": iso3, "raw_reference_period": period}); continue
        seen.add((iso3, year))
        observation_id = stable_id("obs", metric["source_id"], metric["source_indicator_id"], iso3, year)
        accepted.append({"observation_id": observation_id, "country_id": countries[iso3]["country_id"], "iso3": iso3, "reference_period": str(year), "year": year, "metric_id": metric["metric_id"], "value": float(value), "raw_value": value, "modeled_value": None, "unit": metric["unit"], "frequency": metric["frequency"], "source_id": metric["source_id"], "source_dataset_id": metric["source_dataset_id"], "source_indicator_id": metric["source_indicator_id"], "source_indicator": metric["source_indicator_id"], "retrieved_at": retrieved_at, "raw_snapshot_id": snapshot_id, "raw_record_index": index, "transformation_id": metric["transformation"], "pipeline_run_id": run_id})
    return accepted, rejected


def _write_outputs(payload: dict, panel: list[dict], universe: list[dict], rejected: list[dict]) -> list[str]:
    PROCESSED.mkdir(parents=True, exist_ok=True); APP_DATA.mkdir(parents=True, exist_ok=True)
    _write_csv(PROCESSED / "observations.csv", panel); _write_csv(PROCESSED / "countries.csv", universe); _write_csv(PROCESSED / "rejected_observations.csv", rejected)
    metric_dir = APP_DATA / "metrics"; metric_dir.mkdir(parents=True, exist_ok=True)
    ranking_dir = APP_DATA / "rankings"; ranking_dir.mkdir(parents=True, exist_ok=True)
    profile_dir = APP_DATA / "profiles"; profile_dir.mkdir(parents=True, exist_ok=True)
    for directory in (metric_dir, ranking_dir, profile_dir):
        for stale in directory.glob("*.json"):
            stale.unlink()
    by_metric: dict[str, list[dict]] = defaultdict(list)
    for row in panel: by_metric[row["metric_id"]].append(row)
    for metric_id, rows in by_metric.items():
        (metric_dir / f"{metric_id}.json").write_text(json.dumps(rows, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    ranking_assets = {}
    for metric in payload["metrics"]:
        asset = ranking_asset(panel, universe, metric); ranking_assets[metric["metric_id"]] = asset
        (ranking_dir / f"{metric['metric_id']}.json").write_text(json.dumps(asset,separators=(",", ":"),sort_keys=True),encoding="utf-8")
    for country in universe:
        profile = country_profile(panel, universe, payload["metrics"], country["iso3"])
        (profile_dir / f"{country['iso3']}.json").write_text(json.dumps(profile,separators=(",", ":"),sort_keys=True),encoding="utf-8")
    version=payload["meta"].get("asset_version","dev")
    catalog = {"meta": payload["meta"], "countries": payload["countries"], "metrics": payload["metrics"], "sources": payload["sources"], "overview_metric_ids":["gdp_current_usd","gdp_growth_pct","inflation_cpi_pct","unemployment_pct","general_government_gross_debt_pct_gdp"], "observation_shards": {metric_id: f"data/metrics/{metric_id}.json?v={version}" for metric_id in sorted(by_metric)}, "ranking_shards": {metric_id:f"data/rankings/{metric_id}.json?v={version}" for metric_id in sorted(by_metric)}, "profile_shards": {country["iso3"]:f"data/profiles/{country['iso3']}.json?v={version}" for country in universe}}
    (APP_DATA / "catalog.json").write_text(json.dumps(catalog, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    _write_dashboard_json(payload)
    return ["data/processed/dashboard.json", "data/processed/observations.csv", "data/processed/countries.csv", "data/processed/rejected_observations.csv", "app/data/dashboard.json", "app/data/catalog.json", "app/data/metrics/*.json", "app/data/rankings/*.json", "app/data/profiles/*.json"]


def _write_dashboard_json(payload: dict) -> None:
    serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    (PROCESSED / "dashboard.json").write_text(serialized, encoding="utf-8"); (APP_DATA / "dashboard.json").write_text(serialized, encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows: path.write_text("", encoding="utf-8"); return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)


def _code_commit() -> str | None:
    try: return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True,stderr=subprocess.DEVNULL,timeout=2).strip()
    except (subprocess.SubprocessError,OSError): return None


def _display_path(path: Path) -> str:
    try:return str(path.relative_to(ROOT))
    except ValueError:return str(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--start", type=int, default=START_YEAR); parser.add_argument("--end", type=int, default=END_YEAR); args = parser.parse_args()
    result = build(args.start, args.end)
    print(f"Built {len(result['observations']):,} observations for {len(result['countries'])} economies; universe year {result['meta']['reference_year']}.")
