import json
import unittest
from pathlib import Path


class PayloadQualityTests(unittest.TestCase):
    def test_built_payload_contract_if_present(self):
        path = Path(__file__).parents[1] / "app" / "data" / "dashboard.json"
        if not path.exists():
            self.skipTest("pipeline payload has not been built")
        payload = json.loads(path.read_text())
        self.assertEqual(payload["meta"]["universe_size"], 50)
        self.assertEqual(len(payload["countries"]), 50)
        self.assertEqual(len({c["iso3"] for c in payload["countries"]}), 50)
        self.assertTrue(all(o["source_id"] for o in payload["observations"]))
        self.assertTrue(all(o["raw_value"] == o["value"] for o in payload["observations"]))


if __name__ == "__main__":
    unittest.main()
