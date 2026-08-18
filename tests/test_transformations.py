import unittest

from gei.transformations import cagr, latest_by_country, pct_change, rank_desc, rebase


class TransformationTests(unittest.TestCase):
    def test_cagr(self):
        self.assertEqual(round(cagr(121, 100, 2), 8), 10)
        self.assertIsNone(cagr(100, 0, 2))
        self.assertIsNone(cagr(None, 100, 2))

    def test_pct_change(self):
        self.assertAlmostEqual(pct_change(110, 100), 10)
        self.assertIsNone(pct_change(10, 0))

    def test_rank_desc_is_deterministic_and_missing_visible(self):
        self.assertEqual(rank_desc({"B": 5, "A": 5, "C": None}), {"B": 2, "A": 1, "C": None})

    def test_latest_by_country_uses_each_country_latest_not_global_year(self):
        rows = [
            {"iso3": "A", "year": 2022, "metric_id": "x", "value": 1},
            {"iso3": "A", "year": 2023, "metric_id": "x", "value": 2},
            {"iso3": "B", "year": 2022, "metric_id": "x", "value": 3},
        ]
        self.assertEqual(latest_by_country(rows, "x"), {"A": rows[1], "B": rows[2]})

    def test_rebase_preserves_missing_values(self):
        rows = [{"year": 2000, "value": 5}, {"year": 2001, "value": None}, {"year": 2002, "value": 10}]
        self.assertEqual([row["rebased_value"] for row in rebase(rows, 2000)], [100, None, 200])

if __name__ == "__main__":
    unittest.main()
