"""Build the governed map-readiness inventory without inferring geometry or identity."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "data/processed/dashboard.json").read_text())
    display = {row["iso3"] for row in payload["countries"]}
    rows = []
    for entity in payload["ingestion_entities"]:
        flag = entity.get("flag_asset")
        flag_available = bool(flag and (ROOT / "app" / flag).exists())
        governed = entity["iso3"] in display
        status = "MISSING GEOMETRY" if governed else "MISSING GOVERNANCE"
        rows.append({
            "canonical_entity_id": entity["analytical_entity_id"],
            "iso3": entity["iso3"], "iso2": entity.get("iso2"),
            "source_ids": {"imf_weo": entity["iso3"], "world_bank": entity["iso3"] if entity.get("iso2") else None},
            "geometry_id": None, "geometry_available": False,
            "flag_available": flag_available,
            "region_metadata_available": bool(entity.get("region")),
            "mapping_status": status,
            "adjudication_status": "phase_1_1_display_approved" if governed else "worldwide_review_required",
        })
    summary = {}
    for row in rows:
        summary[row["mapping_status"]] = summary.get(row["mapping_status"], 0) + 1
    output = {
        "schema_version": "1.0", "release_id": payload["meta"]["release_id"],
        "geometry_registry_present": False,
        "summary": summary, "entities": rows,
    }
    target = ROOT / "docs/audit/MAP_READINESS.json"
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"Map readiness: {len(rows)} entities; {summary}")


if __name__ == "__main__":
    main()
