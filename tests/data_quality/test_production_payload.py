import json
import unittest
from pathlib import Path

from gei.validation import validate_observations


class ProductionPayloadTests(unittest.TestCase):
    def test_payload_is_structurally_valid(self):
        path=Path(__file__).parents[2]/"app/data/dashboard.json"
        if not path.exists():self.skipTest("dashboard payload not built")
        payload=json.loads(path.read_text())
        if payload.get("meta",{}).get("schema_version")!="2.0":self.skipTest("payload predates hardening build")
        report=validate_observations(payload["observations"],payload["countries"],payload["metrics"])
        self.assertTrue(report.valid,report.errors[:5])


if __name__ == "__main__": unittest.main()
