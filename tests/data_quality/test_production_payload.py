import json
import unittest
from pathlib import Path

from gei.validation import validate_observations


class ProductionPayloadTests(unittest.TestCase):
    def test_payload_is_structurally_valid(self):
        path=Path(__file__).parents[2]/"data/processed/dashboard.json"
        if not path.exists():self.skipTest("dashboard payload not built")
        payload=json.loads(path.read_text())
        if payload.get("meta",{}).get("schema_version") not in {"2.0", "2.1", "2.2", "2.3"}:self.skipTest("payload predates hardening build")
        if payload["meta"]["schema_version"] != "2.3":self.skipTest("payload predates canonical-classification schema")
        report=validate_observations(payload["observations"],payload["ingestion_entities"],payload["metrics"])
        self.assertTrue(report.valid,report.errors[:5])
        if payload["meta"]["schema_version"] in {"2.1", "2.2", "2.3"}:
            self.assertEqual(payload["meta"]["eligibility_policy_version"], "phase_1_1_v1")
            self.assertEqual(payload["meta"]["candidate_universe_complete"], payload["meta"]["schema_version"] in {"2.2", "2.3"})
            catalog=json.loads((Path(__file__).parents[2]/"app/data/catalog.json").read_text())
            self.assertEqual(set(catalog["ranking_shards"]), {m["metric_id"] for m in payload["metrics"]})
            self.assertEqual(payload["meta"]["ingestion_universe_size"], len(payload["ingestion_entities"]))
            self.assertEqual(len(payload["countries"]), 50)


if __name__ == "__main__": unittest.main()
