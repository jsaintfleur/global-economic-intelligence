"""Encode the economist-approved Phase 1 cohort without inferring sovereignty."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "app/data/dashboard.json").read_text())
    countries = json.loads((ROOT / "config/countries.json").read_text())["countries"]
    current = {row["iso3"] for row in payload["countries"]}
    rows = []
    for country in countries:
        included = country["iso3"] in current
        rows.append({
            "analytical_entity_id": f"entity:{country['iso3']}", "display_name": country["canonical_name"],
            "analytical_eligibility": "included" if included else "pending_review",
            "eligibility_policy_version": "phase_1_1_v1", "eligibility_basis": "Approved Phase 1 analytical cohort" if included else "Not reviewed for inclusion in the Phase 1 analytical cohort",
            "effective_from": "2026-08-17", "effective_to": None, "review_owner": "economic_audit_phase_1_1",
            "authoritative_ids": {"world_bank_code": country["world_bank_code"], "imf_weo_code": None, "iso3": country["iso3"], "un_m49": country.get("un_code")},
            "source_references": ["World Bank country dimension", "release_e9182edbdb3e275e19ca"]
        })
    rows.append({"analytical_entity_id":"entity:TWN","display_name":"Taiwan","analytical_eligibility":"pending_review","eligibility_policy_version":"phase_1_1_v1","eligibility_basis":"Source-unavailable in the current World Bank GDP provider; explicit review and approved GDP source mapping required","effective_from":"2026-08-17","effective_to":None,"review_owner":"economic_audit_phase_1_1","authoritative_ids":{"world_bank_code":None,"imf_weo_code":"TWN","iso3":None,"un_m49":None},"source_references":["IMF WEO country code TWN","agent_handoff/CLAUDE_TO_CODEX.md"]})
    document = {"schema_version":"1.0","eligibility_policy_version":"phase_1_1_v1","authority":"Economist-approved Phase 1 cohort; no sovereignty inference","entities":sorted(rows,key=lambda row:row["analytical_entity_id"])}
    (ROOT / "config/analytical_entities.json").write_text(json.dumps(document, indent=2, sort_keys=True)+"\n")


if __name__ == "__main__": main()
