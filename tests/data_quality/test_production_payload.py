import json
import unittest
from pathlib import Path

from gei.validation import validate_observations


class ProductionPayloadTests(unittest.TestCase):
    def test_payload_is_structurally_valid(self):
        path=Path(__file__).parents[2]/"app/data/dashboard.json"
        if not path.exists():self.skipTest("dashboard payload not built")
        payload=json.loads(path.read_text())
        if payload.get("meta",{}).get("schema_version") not in {"2.0", "2.1", "2.2"}:self.skipTest("payload predates hardening build")
        report=validate_observations(payload["observations"],payload["countries"],payload["metrics"])
        self.assertTrue(report.valid,report.errors[:5])
        if payload["meta"]["schema_version"] in {"2.1", "2.2"}:
            self.assertEqual(payload["meta"]["eligibility_policy_version"], "phase_1_1_v1")
            self.assertEqual(payload["meta"]["candidate_universe_complete"], payload["meta"]["schema_version"] == "2.2")
            catalog=json.loads((path.parent/"catalog.json").read_text())
            self.assertEqual(set(catalog["ranking_shards"]), {m["metric_id"] for m in payload["metrics"]})


if __name__ == "__main__": unittest.main()
