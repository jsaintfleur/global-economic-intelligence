import json
import unittest
from pathlib import Path

from gei.validation import ALLOWED_OBSERVATION_CLASSES, REQUIRED_OBSERVATION_FIELDS


ROOT = Path(__file__).resolve().parents[2]


class AuditRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "data/processed/dashboard.json").read_text())
        cls.catalog = json.loads((ROOT / "app/data/catalog.json").read_text())
        cls.js = (ROOT / "app/app.js").read_text()
        cls.html = (ROOT / "app/index.html").read_text()

    def test_a01_ingestion_is_not_the_top50_display_boundary(self):
        self.assertGreaterEqual(len(self.payload["ingestion_entities"]), 190)
        self.assertEqual(len(self.payload["countries"]), 50)
        self.assertEqual(len(self.catalog["display_cohorts"]["top50"]), 50)
        metric_rows = json.loads((ROOT / "app/data/metrics/gdp_current_usd.json").read_text())
        self.assertEqual(len({row["iso3"] for row in metric_rows}), 50)
        build_script = (ROOT / "scripts/build_static.py").read_text()
        self.assertIn('return {"dashboard.json"}', build_script)

    def test_a02_historical_world_ranking_includes_noncurrent_member(self):
        current = set(self.catalog["display_cohorts"]["top50"])
        asset = json.loads((ROOT / "app/data/rankings_worldwide/gdp_current_usd.json").read_text())
        rows = [row for row in asset["rankings"]["2000"]["rows"] if row["rank"]]
        self.assertEqual(asset["ranking_scope"], "contemporaneous_ingestion_universe")
        self.assertTrue(any(row["iso3"] not in current for row in rows))
        self.assertIn("loadWorldwideRanking", self.js)
        self.assertIn("state.worldwideRankings", self.js)
        self.assertIn("contemporaneous eligible ingestion universe", self.js)

    def test_a03_profile_share_is_same_year_only(self):
        self.assertIn("gdpRank?.observation_year===gdpRanking.ranking_year", self.js)
        self.assertIn("SHARE OF ${gdpRanking.ranking_year} ATLAS COHORT GDP", self.js)
        self.assertIn("REAL GROWTH · ${growth?.year", self.js)
        self.assertIn("POPULATION · ${pop?.year", self.js)
        self.assertNotIn("auditedCountry", self.js)

    def test_a04_ranking_rows_preserve_classification_and_provenance(self):
        asset = json.loads((ROOT / "app/data/rankings/gdp_current_usd.json").read_text())
        row = next(row for row in asset["rankings"]["2024"]["rows"] if row["rank"])
        for field in ("observation_class", "observation_year", "source_id", "source_vintage", "coverage_state", "missing_reason"):
            self.assertIn(field, row)

    def test_a05_canonical_schema_is_uniform(self):
        for row in self.payload["observations"]:
            self.assertFalse(REQUIRED_OBSERVATION_FIELDS - row.keys())

    def test_a06_taiwan_unemployment_is_structural_missingness(self):
        asset = json.loads((ROOT / "app/data/rankings/unemployment_pct.json").read_text())
        row = next(row for row in asset["rankings"]["2024"]["rows"] if row["iso3"] == "TWN")
        self.assertEqual(row["missing_reason"], "not_reported_by_source")

    def test_a07_flags_are_local_and_complete_for_display_cohort(self):
        self.assertNotIn("flagcdn.com", self.js)
        for country in self.payload["countries"]:
            self.assertTrue(country["flag_asset"])
            self.assertTrue((ROOT / "app" / country["flag_asset"]).exists())

    def test_a08_taiwan_identity_is_data_not_view_logic(self):
        taiwan = next(row for row in self.payload["countries"] if row["iso3"] == "TWN")
        self.assertEqual(taiwan["iso2"], "TW")
        self.assertNotIn("iso3==='TWN'", self.js)

    def test_a09_preview_has_no_false_production_canonical(self):
        self.assertNotIn("rel=\"canonical\"", self.html)
        self.assertNotIn("global-economic-intelligence.vercel.app", self.html)

    def test_a10_observation_taxonomy_is_governed(self):
        observed = {row["observation_class"] for row in self.payload["observations"]}
        self.assertLessEqual(observed, ALLOWED_OBSERVATION_CLASSES)
        self.assertNotIn("forecast", observed)

    def test_a11_vacuous_rank_movement_is_suppressed(self):
        self.assertIn("nowRank!==oldRank", self.js)
        self.assertIn("has held the #${nowRank} position", self.js)

    def test_a12_sensitive_editorial_states_are_explicit(self):
        taiwan = next(row for row in self.payload["countries"] if row["iso3"] == "TWN")
        self.assertIsNone(taiwan["region"])
        self.assertIn("c.region!=='Not classified'", self.js)
        self.assertIn("higher unemployment is not better", self.js)


if __name__ == "__main__":
    unittest.main()
