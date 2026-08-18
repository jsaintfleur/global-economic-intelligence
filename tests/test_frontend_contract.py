import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js=(ROOT/"app/app.js").read_text(); cls.html=(ROOT/"app/index.html").read_text()

    def test_exact_year_missing_state_and_historical_context(self):
        self.assertIn("Only observations from ${r.ranking_year} receive a rank",self.js)
        self.assertIn("Latest historical context",self.js)
        self.assertIn("Not available for ${r.ranking_year}",self.js)

    def test_url_state_and_coverage_are_first_class(self):
        self.assertIn("new URLSearchParams(location.search)",self.js); self.assertIn("history.pushState",self.js)
        self.assertIn('data-view="coverage"',self.html)

    def test_export_contains_lineage(self):
        for field in ("source_indicator_id","raw_snapshot_id","pipeline_run_id","release_id"): self.assertIn(field,self.js)

if __name__ == "__main__": unittest.main()
