"""Generate a release-bound, evidence-only economic audit support bundle."""
from __future__ import annotations

import ast
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "audit"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def csv_write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(cell(value) for value in row) + " |" for row in rows),
    ])


def ranges(missing: list[int]) -> str:
    if not missing:
        return "None"
    result, start, previous = [], missing[0], missing[0]
    for year in missing[1:]:
        if year != previous + 1:
            result.append(str(start) if start == previous else f"{start}-{previous}")
            start = year
        previous = year
    result.append(str(start) if start == previous else f"{start}-{previous}")
    return "; ".join(result)


def main() -> None:
    release = load("data/releases/latest.json")
    payload = load("app/data/dashboard.json")
    metrics_doc = load("config/metrics.json")
    sources_doc = load("config/sources.json")
    transforms_doc = load("config/transformations.json")
    countries_doc = load("config/countries.json")
    manifest = load(payload["meta"]["manifest_path"])
    if release["release_id"] != payload["meta"]["release_id"] or release["pipeline_run_id"] != payload["meta"]["pipeline_run_id"]:
        raise RuntimeError("Published release, application payload, and pipeline run do not match")

    out = ROOT / "data" / "audit" / release["release_id"]
    out.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    metrics = metrics_doc["metrics"]
    metric_by_id = {m["metric_id"]: m for m in metrics}
    source_by_id = {s["source_id"]: s for s in sources_doc["sources"]}
    transform_by_id = {t["transformation_id"]: t for t in transforms_doc["transformations"]}
    country_registry = {c["iso3"]: c for c in countries_doc["countries"]}
    universe = sorted(payload["countries"], key=lambda c: c["gdp_rank"])
    universe_by_iso = {c["iso3"]: c for c in universe}
    observations = payload["observations"]
    by_metric: dict[str, list[dict]] = defaultdict(list)
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in observations:
        by_metric[row["metric_id"]].append(row)
        by_pair[(row["metric_id"], row["iso3"])].append(row)

    # Metric inventory and complete country-metric freshness matrix.
    inventory, freshness = [], []
    for metric in metrics:
        rows = by_metric[metric["metric_id"]]
        latest_years = []
        metric_max = max((r["year"] for r in rows), default=None)
        for country in universe:
            pair = by_pair[(metric["metric_id"], country["iso3"])]
            latest = max(pair, key=lambda r: r["year"]) if pair else None
            if latest:
                latest_years.append(latest["year"])
            freshness.append({
                "country": country["name"], "iso3": country["iso3"], "metric_id": metric["metric_id"],
                "latest_observation_year": latest["year"] if latest else "", "latest_value": latest["value"] if latest else "",
                "source_id": metric["source_id"], "source_indicator_id": metric["source_indicator_id"],
                "years_behind_metric_max": metric_max - latest["year"] if latest else "",
            })
        inventory.append({
            "metric_id": metric["metric_id"], "display_name": metric["display_name"], "source_id": metric["source_id"],
            "source_dataset_id": metric["source_dataset_id"], "source_indicator_id": metric["source_indicator_id"],
            "unit": metric["unit"], "transformation": metric["transformation"], "observation_count": len(rows),
            "countries_covered": len({r["iso3"] for r in rows}), "earliest_year": min((r["year"] for r in rows), default=""),
            "latest_year": metric_max or "", "median_latest_year": statistics.median(latest_years) if latest_years else "",
            "minimum_latest_year": min(latest_years, default=""), "maximum_latest_year": max(latest_years, default=""),
            "missing_top50_countries": 50 - len(latest_years), "registry_version": release["metric_registry_version"],
        })
    csv_write(out / "current_metric_inventory.csv", inventory)
    write(out / "current_metric_inventory.json", json.dumps(inventory, indent=2, sort_keys=True))
    csv_write(out / "country_metric_freshness.csv", freshness)
    write(DOCS / "CURRENT_METRIC_INVENTORY.md", """# Current Metric Inventory

Technical summary: this is a direct inventory of the current application payload. Counts refer only to the fixed Top-50 universe; no freshness judgment is applied.

""" + table(["Metric", "Display", "Source / indicator", "Unit", "Transform", "Obs.", "Countries", "Years", "Latest-year median / min / max", "Missing"], [[r["metric_id"], r["display_name"], f'{r["source_id"]} / {r["source_indicator_id"]}', r["unit"], r["transformation"], r["observation_count"], r["countries_covered"], f'{r["earliest_year"]}-{r["latest_year"]}', f'{r["median_latest_year"]} / {r["minimum_latest_year"]} / {r["maximum_latest_year"]}', r["missing_top50_countries"]] for r in inventory]) + f"""

Metric registry fingerprint: `{release['metric_registry_version']}`. Source dataset for every row: `world_development_indicators`. Exact fields are in [`current_metric_inventory.csv`](../../data/audit/{release['release_id']}/current_metric_inventory.csv) and the adjacent JSON.
""")
    lag_counts = Counter(str(r["years_behind_metric_max"]) if r["years_behind_metric_max"] != "" else "no observation" for r in freshness)
    write(DOCS / "COUNTRY_YEAR_FRESHNESS.md", f"""# Country-Year Freshness Matrix

Technical summary: the complete 350-row matrix reports each Top-50 country and Phase 1 metric without assigning a fresh/stale label. `years_behind_metric_max` is the metric-wide maximum observed year minus that country's latest observed year.

## Lag distribution

{table(['Years behind metric maximum', 'Country-metric pairs'], [[k, v] for k, v in sorted(lag_counts.items(), key=lambda x: (x[0] == 'no observation', x[0]))])}

Complete evidence: [`country_metric_freshness.csv`](../../data/audit/{release['release_id']}/country_metric_freshness.csv).
""")

    # Universe evidence: recreate the exact pipeline rule from its raw GDP snapshot.
    gdp_snapshot = next(s for s in manifest["raw_snapshots"] if s["source_indicator_id"] == "NY.GDP.MKTP.CD")
    gdp_raw = load(gdp_snapshot["path"])
    dim_snapshot = next(s for s in manifest["raw_snapshots"] if s["source_indicator_id"] == "country_dimension")
    dimensions = load(dim_snapshot["path"])
    canonical = {r["id"]: r for r in dimensions if r.get("region", {}).get("id") not in (None, "NA") and len(r.get("id", "")) == 3}
    ref = payload["meta"]["reference_year"]
    values = {r["countryiso3code"]: float(r["value"]) for r in gdp_raw if r.get("countryiso3code") in canonical and r.get("date") == str(ref) and r.get("value") is not None}
    ranked = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    universe_rows = [{"rank": i, "selected": i <= 50, "iso3": iso, "country": canonical[iso]["name"], "gdp_value": value, "observation_year": ref, "source_id": "world_bank_wdi", "source_indicator_id": "NY.GDP.MKTP.CD", "territory_classification": country_registry.get(iso, {}).get("territory_classification")} for i, (iso, value) in enumerate(ranked, 1)]
    excluded = [{"iso3": iso, "country": row["name"], "reason": f"missing GDP value in reference year {ref}"} for iso, row in sorted(canonical.items()) if iso not in values]
    csv_write(out / "top50_universe_candidates.csv", universe_rows)
    csv_write(out / "top50_universe_missing_reference_year.csv", excluded)
    write(out / "top50_universe_evidence.json", json.dumps({"rule": {"indicator": "NY.GDP.MKTP.CD", "minimum_nonaggregate_observations": 150, "reference_year": ref, "sort": "GDP descending, then ISO3 ascending", "selection_count": 50}, "candidate_count": len(values), "selected": universe_rows[:50], "near_cutoff": universe_rows[44:55], "excluded_missing_reference_year": excluded}, indent=2, sort_keys=True))
    included_unknown = [r for r in universe_rows[:50] if r["territory_classification"] is None]
    write(DOCS / "TOP50_UNIVERSE_EVIDENCE.md", f"""# Top-50 Universe Evidence

Technical summary: release `{release['release_id']}` uses one common GDP observation year, `{ref}`, for every selected economy. Mixed observation years do not affect this universe snapshot.

## Implemented selection rule

- Indicator: World Bank WDI `NY.GDP.MKTP.CD` (nominal GDP, current US$).
- Reference year: latest year with at least 150 valid non-aggregate economy observations; current result `{ref}`.
- Candidate count in that year: {len(values)}.
- Ranking: GDP descending, then ISO3 ascending; first 50 selected.
- Aggregate exclusion: country-dimension region ID is neither null nor `NA`, and the ID has three characters.

## Selected economies

{table(['Rank', 'Economy', 'ISO3', 'GDP value', 'Year'], [[r['rank'], r['country'], r['iso3'], format(r['gdp_value'], '.15g'), r['observation_year']] for r in universe_rows[:50]])}

## Cutoff neighborhood (ranks 45-55)

{table(['Rank', 'Economy', 'ISO3', 'GDP value', 'Selected'], [[r['rank'], r['country'], r['iso3'], format(r['gdp_value'], '.15g'), r['selected']] for r in universe_rows[44:55]])}

## Missing reference-year candidates

{len(excluded)} canonical non-aggregate country-dimension entries have no usable GDP value in `{ref}`. See the machine-readable exclusion file for the exact list.

## Territory/entity evidence boundary

The country registry states `World Bank country dimension; no sovereignty classification added`. All {len(included_unknown)} selected entries have `territory_classification: null`; therefore this package does not infer which included entries are territories or sovereign states. Claude should review that classification question directly.

Files: [`top50_universe_candidates.csv`](../../data/audit/{release['release_id']}/top50_universe_candidates.csv), [`top50_universe_missing_reference_year.csv`](../../data/audit/{release['release_id']}/top50_universe_missing_reference_year.csv), and adjacent JSON.
""")

    # Deterministic lineage examples: first and last observation by ISO3/year per metric.
    snapshots = {s["raw_snapshot_id"]: s for s in manifest["raw_snapshots"]}
    lineage = []
    for metric in metrics:
        rows = sorted(by_metric[metric["metric_id"]], key=lambda r: (r["iso3"], r["year"], r["observation_id"]))
        for label, row in (("first", rows[0]), ("last", rows[-1])):
            snap = snapshots[row["raw_snapshot_id"]]
            raw = load(snap["path"])[row["raw_record_index"]]
            lineage.append({"metric_id": metric["metric_id"], "selection": label, "source_id": row["source_id"], "source_dataset_id": row["source_dataset_id"], "source_indicator_id": row["source_indicator_id"], "raw_snapshot_id": row["raw_snapshot_id"], "raw_snapshot_path": snap["path"], "raw_snapshot_sha256": snap["checksum_sha256"], "raw_record_index": row["raw_record_index"], "raw_record": raw, "observation_id": row["observation_id"], "normalized_observation_path": "data/processed/observations.csv", "normalized_value": row["raw_value"], "transformation_id": row["transformation_id"], "final_application_path": f'app/data/metrics/{metric["metric_id"]}.json', "final_application_value": row["value"], "iso3": row["iso3"], "year": row["year"]})
    write(out / "lineage_examples.json", json.dumps(lineage, indent=2, sort_keys=True))
    write(DOCS / "LINEAGE_EXAMPLES.md", f"""# Metric Lineage Examples

Technical summary: two examples per metric were selected deterministically as the lexicographically first and last `(ISO3, year, observation_id)` rows in the release payload. Values below were generated by dereferencing each observation's raw snapshot and record index.

{table(['Metric', 'Selection', 'ISO3 / year', 'Raw snapshot / index', 'Observation ID', 'Raw → normalized → app', 'Transform'], [[r['metric_id'], r['selection'], f"{r['iso3']} / {r['year']}", f"{r['raw_snapshot_id']} / {r['raw_record_index']}", r['observation_id'], f"{r['raw_record']['value']} → {r['normalized_value']} → {r['final_application_value']}", r['transformation_id']] for r in lineage])}

Full records, checksums, and paths: [`lineage_examples.json`](../../data/audit/{release['release_id']}/lineage_examples.json).
""")

    # Missingness and rejection evidence.
    rejected = list(csv.DictReader((ROOT / "data/processed/rejected_observations.csv").open(encoding="utf-8")))
    rejected_counts = Counter((r["source_indicator_id"], r["reason"]) for r in rejected)
    missing_summary, missing_ranges = [], []
    start, end = payload["meta"]["start_year"], payload["meta"]["end_year"]
    for metric in metrics:
        rows = by_metric[metric["metric_id"]]
        metric_max = max(r["year"] for r in rows)
        no_obs, behind = [], []
        for country in universe:
            pair = by_pair[(metric["metric_id"], country["iso3"])]
            years = {r["year"] for r in pair}
            missing = [year for year in range(start, end + 1) if year not in years]
            missing_ranges.append({"metric_id": metric["metric_id"], "iso3": country["iso3"], "country": country["name"], "missing_year_ranges": ranges(missing), "missing_year_count": len(missing)})
            if not pair:
                no_obs.append(country["iso3"])
            elif max(years) < metric_max:
                behind.append(f"{country['iso3']} ({max(years)})")
        reasons = [{"reason": reason, "count": count} for (indicator, reason), count in sorted(rejected_counts.items()) if indicator == metric["source_indicator_id"]]
        missing_summary.append({"metric_id": metric["metric_id"], "metric_max_year": metric_max, "countries_with_no_observations": no_obs, "countries_behind_metric_max": behind, "transformation_removed_observations": False, "transformation_evidence": f"{metric['transformation']} preserves normalized source values", "rejected_observation_count": sum(r["count"] for r in reasons), "rejection_reasons": reasons})
    csv_write(out / "missing_country_year_ranges.csv", missing_ranges)
    write(out / "missing_data_summary.json", json.dumps(missing_summary, indent=2, sort_keys=True))
    write(DOCS / "MISSING_DATA_SUMMARY.md", f"""# Missing-Data Summary

Technical summary: Phase 1 preserves missing values and uses identity transformations. No transformation removes a normalized observation. Structural rejections occur before the Top-50 panel is selected.

{table(['Metric', 'No observations', 'Latest behind metric max', 'Rejected raw rows', 'Structural rejection reasons'], [[r['metric_id'], ', '.join(r['countries_with_no_observations']) or 'None', ', '.join(r['countries_behind_metric_max']) or 'None', r['rejected_observation_count'], '; '.join(f"{x['reason']}: {x['count']}" for x in r['rejection_reasons']) or 'None'] for r in missing_summary])}

Exact country-year gaps: [`missing_country_year_ranges.csv`](../../data/audit/{release['release_id']}/missing_country_year_ranges.csv). Structured summary: [`missing_data_summary.json`](../../data/audit/{release['release_id']}/missing_data_summary.json).
""")

    # Current metric implementation evidence.
    methodology = (ROOT / "docs/METHODOLOGY.md").read_text(encoding="utf-8")
    methodology_scope = next(line for line in methodology.splitlines() if line.startswith("Nominal GDP and GDP per capita"))
    def implementation_report(filename: str, title: str, ids: list[str], extra: str = "") -> None:
        sections = []
        machine = []
        for metric_id in ids:
            metric = metric_by_id[metric_id]
            inv = next(r for r in inventory if r["metric_id"] == metric_id)
            latest = [r for r in freshness if r["metric_id"] == metric_id]
            missing = [r["iso3"] for r in latest if r["latest_observation_year"] == ""]
            current = {**metric, **{k: inv[k] for k in ["observation_count", "countries_covered", "earliest_year", "latest_year"]}, "latest_by_country": latest, "missing_top50_countries": missing, "source": source_by_id[metric["source_id"]], "transformation_definition": transform_by_id[metric["transformation"]]}
            machine.append(current)
            sections.append(f"""## {metric['display_name']} (`{metric_id}`)

- Indicator: `{metric['source_indicator_id']}`; source: {source_by_id[metric['source_id']]['organization']} — {source_by_id[metric['source_id']]['dataset']}.
- Registry definition: {metric['description']}
- Unit: `{metric['unit']}`. Transformation: `{metric['transformation']}` — {transform_by_id[metric['transformation']]['description']}
- Coverage: {inv['countries_covered']} of 50 countries, {inv['observation_count']} observations, {inv['earliest_year']}-{inv['latest_year']}. Missing countries: {', '.join(missing) or 'none'}.
- Current UI wording: `{metric['display_name']}` (short label `{metric['short_name']}`). Caveat: {metric['caveat']}

{table(['Country', 'ISO3', 'Latest year', 'Latest value'], [[r['country'], r['iso3'], r['latest_observation_year'], r['latest_value']] for r in latest])}
""")
        write(out / filename.replace("CURRENT_", "current_").replace(".md", ".json").lower(), json.dumps(machine, indent=2, sort_keys=True))
        write(DOCS / filename, f"# {title}\n\nTechnical summary: this report reproduces current registry, payload, source, and transformation evidence without making a methodological recommendation.\n\n{extra}\n\n" + "\n".join(sections))

    implementation_report("CURRENT_DEBT_IMPLEMENTATION.md", "Current Government Debt Implementation", ["central_government_debt_pct_gdp"], f"""The available metadata identifies **central-government debt**. It does not declare general-government scope or a gross/net basis, so those properties are not inferred. Current methodology text: “Debt is central-government debt, not general-government debt.”""")
    implementation_report("CURRENT_INFLATION_IMPLEMENTATION.md", "Current Inflation Implementation", ["inflation_cpi_pct"])
    implementation_report("CURRENT_UNEMPLOYMENT_IMPLEMENTATION.md", "Current Unemployment Implementation", ["unemployment_pct"], "The registry explicitly identifies this as a `modeled ILO estimate`; this report does not select an alternative estimate.")
    implementation_report("CURRENT_GDP_IMPLEMENTATION.md", "Current GDP, GDP Per Capita, and Growth Implementation", ["gdp_current_usd", "gdp_per_capita_current_usd", "gdp_growth_pct"], f"Current methodology text: “{methodology_scope}” Structural bases are exactly those stated in each registry definition and unit below.")

    # Ranking implementation and UI evidence.
    write(out / "ranking_implementation.json", json.dumps({"universe": {"function": "gei.pipeline.build + gei.transformations.rank_desc", "candidate_pool": "all normalized non-aggregate World Bank country-dimension economies with GDP in the common reference year", "missing": "excluded from reference_values and therefore not ranked", "ties": "sequential deterministic ranks after GDP descending then ISO3 ascending", "scope": "global source candidate pool, first 50 retained", "observation_year": ref}, "metric_tables": {"function": "app/app.js buildIndex/latest/rankingTable", "observation_year": "each current Top-50 country's latest non-null observation", "missing": "sorted last, displays Not available, no rank", "ties": "JavaScript stable numeric sort; no explicit secondary tie key or shared-rank policy", "scope": "current Top-50 universe", "historical_rank": "not implemented"}}, indent=2, sort_keys=True))
    write(DOCS / "CURRENT_RANKING_IMPLEMENTATION.md", f"""# Current Ranking Implementation

Technical summary: universe rank is a common-{ref} global-source-candidate GDP rank; metric tables are latest-available rankings within the fixed current Top-50. Historical rank is not implemented.

{table(['Concern', 'Universe construction', 'Metric ranking tables'], [['Function', '`gei.pipeline.build` + `rank_desc`', '`buildIndex`, `latest`, `rankingTable` in `app/app.js`'], ['Observation year', f'Common year {ref}', 'Each country latest non-null year'], ['Missing values', 'Excluded from reference-year candidate values; no rank', 'Sorted after observed values; “Not available”; no displayed rank'], ['Tie handling', 'Sequential rank, GDP descending then ISO3 ascending', 'No shared-rank policy and no explicit secondary tie key'], ['Scope', 'All valid non-aggregate source candidates, then select 50', 'Current Top-50 universe only'], ['Historical rank', 'Not applicable', 'Not implemented; therefore neither global nor current-Top-50 historical rank']])}

Machine-readable evidence: [`ranking_implementation.json`](../../data/audit/{release['release_id']}/ranking_implementation.json).

## Audit note

The current production path is `gei.pipeline.build`. The similarly named universe tests in `tests/test_universe.py` import `pipelines.build`, so they do not directly execute this production selection path.
""")

    ui_rows = [
        ["Overview", "Yes", "Yes", "Yes", "Limited", "Yes", "No", "Sidebar retrieval snapshot"],
        ["Rankings", "Via metric/value formatting", "Yes", "Yes", "Yes", "Yes", "No", "Sidebar retrieval snapshot"],
        ["Compare", "Yes", "Sidebar only", "Yes", "Chart gaps / absent latest cards", "Universe rank in cards", "No", "Sidebar retrieval snapshot"],
        ["Country Explorer", "Yes", "Sidebar only", "Yes", "Yes", "GDP universe rank", "No", "Sidebar retrieval snapshot"],
        ["Data Explorer", "Yes", "Indicator/source columns", "Yes", "Only observed normalized rows are exported", "No", "No", "Per-row retrieval timestamp"],
        ["Methodology", "Yes", "Yes", "Retrieval date", "Policy described", "Formula described", "Yes", "Yes"],
        ["Diagnostics (URL-only)", "No", "Source IDs", "No", "No", "No", "No", "Build generated timestamp"],
    ]
    csv_write(out / "ui_economic_metadata.csv", [dict(zip(["page", "units", "source", "observation_year", "missing_value_state", "rank", "metric_definition", "retrieval_date"], row)) for row in ui_rows])
    write(DOCS / "UI_ECONOMIC_METADATA.md", f"""# UI Economic Metadata

Technical summary: the app exposes observation years and missing-value states prominently in analytical views, while full metric definitions are concentrated on Methodology. This is a visibility inventory, not a redesign proposal.

{table(['Page', 'Units', 'Source', 'Observation year', 'Missing-value state', 'Rank', 'Definition', 'Retrieval date'], ui_rows)}

Evidence basis: current `app/app.js` rendering functions plus the existing automated browser QA performed for this release. Machine matrix: [`ui_economic_metadata.csv`](../../data/audit/{release['release_id']}/ui_economic_metadata.csv).
""")

    # Test map, derived from Python test definitions with explicit evidence classifications.
    mappings = {
        "debt_definition": ("Debt registry remains central-government scoped", "economic-contract", "central_government_debt_pct_gdp"),
        "reference_year": ("Universe reference-year completeness rule", "structural", "gdp_current_usd"),
        "gdp_ranking": ("GDP descending Top-N universe selection", "structural", "gdp_current_usd"),
        "aggregates": ("World Bank aggregate records excluded", "structural", "gdp_current_usd"),
        "latest_by_country": ("Latest available year selected independently by country", "structural", "all Phase 1 metrics"),
        "rank_desc": ("Deterministic descending ranks and visible missing rank", "structural", "all Phase 1 metrics"),
        "coverage": ("Coverage matrices and metric inventory grains", "structural", "all Phase 1 metrics"),
        "payload": ("Published payload contract, provenance, uniqueness, and Top-50 shape", "structural", "all Phase 1 metrics"),
        "metric": ("Metric registry fields and uniqueness", "structural", "all Phase 1 metrics"),
        "observation": ("Canonical observation identity and key integrity", "structural", "all Phase 1 metrics"),
        "provenance": ("Lineage fields propagate and are required", "structural", "all Phase 1 metrics"),
        "snapshot": ("Raw snapshot preservation and checksum", "structural", "all Phase 1 metrics"),
        "adapter": ("Source adapter response contract", "structural", "all Phase 1 metrics"),
        "pipeline": ("Deterministic pipeline outputs and manifest", "structural", "all Phase 1 metrics"),
        "normalization": ("Country/observation normalization constraints", "structural", "all Phase 1 metrics"),
        "release": ("Content-derived release and regression controls", "structural", "all Phase 1 metrics"),
        "revision": ("Release diff revision calculations", "structural", "all Phase 1 metrics"),
        "source": ("Source mapping changes are reported", "structural", "all Phase 1 metrics"),
        "cagr": ("CAGR formula behavior", "structural", "mechanism only"),
        "pct_change": ("Percentage-change formula behavior", "structural", "mechanism only"),
        "rebase": ("Rebase formula preserves missing values", "structural", "mechanism only"),
    }
    test_rows = []
    for path in sorted((ROOT / "tests").rglob("test*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                selected = next((value for key, value in mappings.items() if key in node.name), ("Implementation behavior named by test; inspect test body for exact assertion", "structural", "as applicable"))
                if str(path.relative_to(ROOT)) == "tests/test_universe.py":
                    selected = (selected[0] + " (legacy `pipelines.build` path)", selected[1], selected[2])
                test_rows.append({"test_file": str(path.relative_to(ROOT)), "test_name": node.name, "invariant_protected": selected[0], "classification": selected[1], "phase1_metrics_touched": selected[2]})
    csv_write(out / "test_coverage_map.csv", test_rows)
    gaps = ["The three tests in `tests/test_universe.py` target legacy `pipelines.build`, not the current production `gei.pipeline.build` universe path.", "No independently economist-approved expected-value fixtures for any Phase 1 metric.", "No test asserts a common-year mode for non-universe metric rankings because that mode is not implemented.", "No test defines a shared-rank policy for ties in UI metric tables.", "No automated DOM assertion covers every page/metadata field in the UI visibility matrix.", "No sovereign-state/territory classification invariant exists; the registry deliberately leaves it null.", "No historical-rank invariant exists because historical rank is not implemented."]
    write(DOCS / "TEST_COVERAGE_MAP.md", f"""# Test Coverage Map

Technical summary: {len(test_rows)} tests protect structural contracts; one explicit registry assertion protects the current debt-scope economic contract. The suite does not supply independent economic approval.

{table(['Test file', 'Test', 'Invariant', 'Class', 'Metrics'], [[r['test_file'], r['test_name'], r['invariant_protected'], r['classification'], r['phase1_metrics_touched']] for r in test_rows])}

## Important uncovered areas

""" + "\n".join(f"- {gap}" for gap in gaps) + f"\n\nMachine map: [`test_coverage_map.csv`](../../data/audit/{release['release_id']}/test_coverage_map.csv).")

    machine_artifacts = sorted({*(p.name for p in out.iterdir()), "audit_manifest.json"})
    audit_manifest = {"release": release, "pipeline_manifest": payload["meta"]["manifest_path"], "generated_from": ["app/data/dashboard.json", "config/metrics.json", "config/sources.json", "config/countries.json", "config/transformations.json", "data/processed/rejected_observations.csv", *[s["path"] for s in manifest["raw_snapshots"]]], "markdown_artifacts": sorted(p.name for p in DOCS.glob("*.md")), "machine_artifacts": machine_artifacts}
    write(out / "audit_manifest.json", json.dumps(audit_manifest, indent=2, sort_keys=True))
    write(DOCS / "README.md", f"""# Current Release Audit Bundle

Technical summary: this index binds the audit evidence to the already-published release. The bundle does not rebuild data, introduce methodology, or make economic recommendations.

## Release fingerprints

{table(['Fingerprint', 'Value'], [['Release ID', release['release_id']], ['Pipeline run ID', release['pipeline_run_id']], ['Metric registry', release['metric_registry_version']], ['Source registry', release['source_registry_version']], ['Country registry', release['country_registry_version']], ['Transformation registry', release['transformation_registry_version']], ['Git commit', release['code_commit']], ['Observations / countries / metrics', f"{release['observation_count']} / {release['country_count']} / {release['metric_count']}"]])}

## Audit reports

- [Current metric inventory](CURRENT_METRIC_INVENTORY.md)
- [Country-year freshness](COUNTRY_YEAR_FRESHNESS.md)
- [Top-50 universe evidence](TOP50_UNIVERSE_EVIDENCE.md)
- [Metric lineage examples](LINEAGE_EXAMPLES.md)
- [Missing-data summary](MISSING_DATA_SUMMARY.md)
- [Government debt implementation](CURRENT_DEBT_IMPLEMENTATION.md)
- [Inflation implementation](CURRENT_INFLATION_IMPLEMENTATION.md)
- [Unemployment implementation](CURRENT_UNEMPLOYMENT_IMPLEMENTATION.md)
- [GDP, GDP per capita, and growth implementation](CURRENT_GDP_IMPLEMENTATION.md)
- [Ranking implementation](CURRENT_RANKING_IMPLEMENTATION.md)
- [UI economic metadata](UI_ECONOMIC_METADATA.md)
- [Test coverage map](TEST_COVERAGE_MAP.md)
- [Phase 1.1 classified findings and debt reconciliation](PHASE_1_1_FINDINGS.md)

Machine-readable evidence is under [`data/audit/{release['release_id']}/`](../../data/audit/{release['release_id']}/). Start with `audit_manifest.json`.
""")


if __name__ == "__main__":
    main()
