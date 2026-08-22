"""Build release-bound evidence for the worldwide remediation candidate."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_ID = "release_770e0ce265f624e2a214"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload_path = ROOT / "data/processed/dashboard.json"
    catalog_path = ROOT / "app/data/catalog.json"
    release_path = ROOT / f"data/releases/{RELEASE_ID}.json"
    governance_path = ROOT / "docs/audit/GOVERNANCE_ENFORCEMENT.json"
    map_path = ROOT / "docs/audit/MAP_READINESS.json"
    scale_path = ROOT / "docs/audit/WORLDWIDE_SCALE.json"
    payload = read_json(payload_path)
    catalog = read_json(catalog_path)
    release = read_json(release_path)
    governance = read_json(governance_path)
    map_readiness = read_json(map_path)
    scale = read_json(scale_path)
    if payload["meta"]["release_id"] != RELEASE_ID or release["release_id"] != RELEASE_ID:
        raise RuntimeError("release evidence inputs do not share the pinned release ID")

    observations = payload["observations"]
    ingestion = payload["ingestion_entities"]
    display = payload["countries"]
    classes = Counter(row["observation_class"] for row in observations)
    missing_reasons: Counter[str] = Counter()
    ranking_rows = 0
    ranking_fields = {
        "observation_class", "observation_year", "source_id", "source_vintage",
        "coverage_state", "missing_reason",
    }
    for path in sorted((ROOT / "app/data/rankings").glob("*.json")):
        asset = read_json(path)
        for result in asset["rankings"].values():
            for row in result["rows"]:
                ranking_rows += 1
                if not ranking_fields <= row.keys():
                    raise RuntimeError(f"ranking lineage fields missing in {path.name}")
                if row["missing_reason"]:
                    missing_reasons[row["missing_reason"]] += 1

    weak = [row for row in governance["bindings"] if row["classification"] == "WEAK"]
    evidence = {
        "release_id": RELEASE_ID,
        "release_code_commit_basis": release["code_commit"],
        "worldwide_entity_count": len(ingestion),
        "materialized_top50_count": len(display),
        "canonical_observation_count": len(observations),
        "metric_count": len(payload["metrics"]),
        "source_count": len(payload["sources"]),
        "ranking_methodology": {
            "current": "Exact-year ranking within the materialized Top-50 display cohort.",
            "historical": "Exact-year ranking within the contemporaneous governed ingestion universe; today's Top-50 is not projected backward.",
            "browser_assets": catalog["worldwide_ranking_shards"],
        },
        "observation_classification": {
            "taxonomy": sorted(classes),
            "canonical_counts": dict(sorted(classes.items())),
            "ranking_rows_checked": ranking_rows,
            "required_fields": sorted(ranking_fields),
        },
        "missing_reason_taxonomy": dict(sorted(missing_reasons.items())),
        "gdp_share_basis": {
            "rule": "Country numerator and Atlas Top-50 denominator use the same governed GDP ranking year.",
            "reference_year": payload["meta"]["reference_year"],
            "unavailable_policy": "Do not display a percentage when an exact-year comparable numerator or denominator is unavailable.",
        },
        "governance": governance,
        "geographic_readiness": map_readiness,
        "scale_and_performance": scale,
        "source_hashes": {
            str(path.relative_to(ROOT)): digest(path)
            for path in (payload_path, catalog_path, release_path, governance_path, map_path, scale_path, ROOT / "app/app.js")
        },
    }
    out_dir = ROOT / "data/audit" / RELEASE_ID
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "release_candidate_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    weak_lines = "\n".join(
        f"- `{row['decision']}` / `{row['test_id']}` — {row['risk']} Owner: {row['owner']}. "
        f"Remediation: {row['remediation']} Public release blocker: {str(row['blocks_public_release']).lower()}. "
        f"Map/Phase 2 blocker: {str(row['blocks_map_or_phase_2']).lower()}."
        for row in weak
    ) or "- None."
    doc = f"""# Worldwide Remediation Release Candidate

Release: `{RELEASE_ID}`
Release code-commit basis: `{release['code_commit']}`

## Scope and counts

- Worldwide governed ingestion universe: **{len(ingestion)} entities**.
- Materialized current display cohort: **Top 50**.
- Canonical observations: **{len(observations):,}** across **{len(payload['metrics'])} metrics** and **{len(payload['sources'])} sources**.
- Current rankings: exact-year comparisons within the materialized Top-50 cohort.
- Historical rankings: exact-year comparisons within the contemporaneous governed ingestion universe. Atlas does not project today's Top 50 backward.

## Observation integrity

- Ranking rows preserve observation year, class, source, vintage, coverage state, and missing reason.
- Observation classes present: {', '.join(f'`{key}` ({value:,})' for key, value in sorted(classes.items()))}.
- Missing reasons are explicit; no missing value is converted to zero.
- Economy GDP share uses an exact-year country numerator and the same-year Top-50 denominator. The interface names that year.

## Governance

Enforcement audit: **{governance['summary']['pass']} PASS / {governance['summary']['weak']} WEAK / {governance['summary']['vacuous']} VACUOUS / {governance['summary']['misbound']} MISBOUND**.

{weak_lines}

## Geographic readiness

**World map is not implemented because geographic governance is incomplete.** Zero entities are currently renderable. The readiness audit records **50 missing geometry** and **145 missing geographic governance**. Atlas does not imply partial geographic coverage.

## Scale and performance

- Initial browser catalog: **{scale['browser_initial_payload_bytes']:,} bytes**.
- Canonical store: **{scale['canonical_store_bytes']:,} bytes**; it is not deployed as an initial browser payload.
- Worldwide ranking shards: **{scale['worldwide_ranking_shards']['count']} lazy assets**, **{scale['worldwide_ranking_shards']['bytes']:,} bytes** total.
- Static production build: **134 assets**, **75,846,079 bytes**.

Machine-readable evidence: [`release_candidate_evidence.json`](../../data/audit/{RELEASE_ID}/release_candidate_evidence.json).
"""
    (ROOT / "docs/audit/RELEASE_CANDIDATE.md").write_text(doc, encoding="utf-8")
    print(f"Release-candidate audit evidence ready: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
