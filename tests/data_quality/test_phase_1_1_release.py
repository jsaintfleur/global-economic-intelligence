import json
import unittest
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Phase11ReleaseEvidenceTests(unittest.TestCase):
    def ranking(self, metric_id):
        return json.loads((ROOT / "app" / "data" / "rankings" / f"{metric_id}.json").read_text())

    @pytest.mark.decision("D-002")
    @pytest.mark.test_id("TEST-U-005")
    @pytest.mark.test_id("TEST-F-001")
    def test_inflation_missing_2025_is_not_backfilled(self):
        asset = self.ranking("inflation_cpi_pct")
        self.assertEqual(asset["default_ranking_year"], 2024)
        self.assertNotIn("2025", asset["rankings"])
        ranking = asset["rankings"]["2024"]
        for iso3 in ("USA", "ARG"):
            row = next(row for row in ranking["rows"] if row["iso3"] == iso3)
            self.assertIsNotNone(row["rank"]); self.assertIsNotNone(row["value"])
            self.assertEqual(row["observation_year"], 2024)
            self.assertEqual(row["ranking_year"], 2024)

    def test_general_government_debt_has_complete_same_year_coverage(self):
        coverage = json.loads((ROOT / "app" / "data" / "coverage.json").read_text())
        debt = next(row for row in coverage["inventory"] if row["metric_id"] == "general_government_gross_debt_pct_gdp")
        self.assertEqual((debt["ever_observed_country_count"], debt["ranking_year_observed_country_count"]), (50, 50))
        self.assertEqual(debt["ranking_year"], 2024)
        ranking = self.ranking("general_government_gross_debt_pct_gdp")["rankings"]["2024"]
        self.assertEqual(ranking["ranked_entity_count"], 50)
        self.assertEqual({row["source_indicator_id"] for row in json.loads((ROOT/"app/data/metrics/general_government_gross_debt_pct_gdp.json").read_text())}, {"GGXWDG_NGDP"})

    def test_same_year_gdp_uses_complete_imf_candidate_universe(self):
        payload = json.loads((ROOT / "app" / "data" / "dashboard.json").read_text())
        cohort = {c["iso3"] for c in payload["countries"]}; reference_year = payload["meta"]["reference_year"]
        observed = {o["iso3"] for o in payload["observations"] if o["metric_id"] == "gdp_current_usd" and o["year"] == reference_year}
        self.assertTrue(cohort <= observed); self.assertTrue(payload["meta"]["candidate_universe_complete"])
        taiwan = next(row for row in payload["countries"] if row["iso3"] == "TWN")
        self.assertEqual(taiwan["gdp_rank"], 22)
        self.assertEqual(payload["meta"]["universe_provider_id"], "imf_weo")

if __name__ == "__main__": unittest.main()
