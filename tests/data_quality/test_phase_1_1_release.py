import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Phase11ReleaseEvidenceTests(unittest.TestCase):
    def ranking(self, metric_id):
        return json.loads((ROOT / "app" / "data" / "rankings" / f"{metric_id}.json").read_text())

    def test_inflation_missing_2025_is_not_backfilled(self):
        ranking = self.ranking("inflation_cpi_pct")["rankings"]["2025"]
        for iso3 in ("USA", "ARG"):
            row = next(row for row in ranking["rows"] if row["iso3"] == iso3)
            self.assertIsNone(row["rank"]); self.assertIsNone(row["value"])
            self.assertEqual(row["latest_historical_year"], 2024)
            self.assertEqual(row["recency_status"], "prior_year"); self.assertEqual(row["lag_years"], 1)

    def test_debt_ever_observed_and_same_year_coverage_are_distinct(self):
        coverage = json.loads((ROOT / "app" / "data" / "coverage.json").read_text())
        debt = next(row for row in coverage["inventory"] if row["metric_id"] == "central_government_debt_pct_gdp")
        self.assertEqual((debt["ever_observed_country_count"], debt["ranking_year_observed_country_count"]), (35, 15))
        self.assertEqual(debt["ranking_year"], 2024)
        ranking = self.ranking("central_government_debt_pct_gdp")["rankings"]["2024"]
        self.assertEqual(ranking["ranked_entity_count"], 15)
        germany = next(row for row in ranking["rows"] if row["iso3"] == "DEU")
        china = next(row for row in ranking["rows"] if row["iso3"] == "CHN")
        self.assertEqual((germany["latest_historical_year"], germany["recency_status"]), (1990, "historical"))
        self.assertIsNone(germany["rank"]); self.assertEqual(china["recency_status"], "unavailable"); self.assertIsNone(china["rank"])

    def test_same_year_gdp_does_not_imply_complete_candidate_universe(self):
        payload = json.loads((ROOT / "app" / "data" / "dashboard.json").read_text())
        cohort = {c["iso3"] for c in payload["countries"]}; reference_year = payload["meta"]["reference_year"]
        observed = {o["iso3"] for o in payload["observations"] if o["metric_id"] == "gdp_current_usd" and o["year"] == reference_year}
        self.assertTrue(cohort <= observed); self.assertFalse(payload["meta"]["candidate_universe_complete"])
        registry = json.loads((ROOT / "config" / "analytical_entities.json").read_text())
        taiwan = next(row for row in registry["entities"] if row["analytical_entity_id"] == "entity:TWN")
        self.assertEqual(taiwan["analytical_eligibility"], "pending_review")
        self.assertIsNone(taiwan["authoritative_ids"]["world_bank_code"])
        self.assertEqual(taiwan["authoritative_ids"]["imf_weo_code"], "TWN")

if __name__ == "__main__": unittest.main()
