import unittest
import pytest

from gei.analytics import change_value, country_profile, indexed_trajectory, rank_metric_year, recency


COUNTRIES=[{"country_id":"country:AAA","analytical_entity_id":"entity:AAA","iso3":"AAA","name":"A"},{"country_id":"country:BBB","analytical_entity_id":"entity:BBB","iso3":"BBB","name":"B"}]


class AnalyticsTests(unittest.TestCase):
    @pytest.mark.decision("D-002")
    @pytest.mark.test_id("TEST-U-005")
    def test_exact_year_ranking_has_no_historical_fallback(self):
        rows=[{"metric_id":"x","iso3":"AAA","year":2025,"value":1},{"metric_id":"x","iso3":"BBB","year":2024,"value":100}]
        result=rank_metric_year(rows,COUNTRIES,"x",2025)
        self.assertEqual(result["ranked_entity_count"],1);self.assertEqual(result["rows"][0]["iso3"],"AAA")
        missing=next(row for row in result["rows"] if row["iso3"]=="BBB")
        self.assertIsNone(missing["rank"]);self.assertIsNone(missing["value"]);self.assertEqual(missing["latest_historical_value"],100)

    @pytest.mark.decision("D-002")
    @pytest.mark.test_id("TEST-F-001")
    def test_recency_classification(self):
        self.assertEqual(recency(2025,2025)["recency_status"],"current_year")
        self.assertEqual(recency(2024,2025)["recency_status"],"prior_year")
        self.assertEqual(recency(1990,2024)["lag_years"],34);self.assertEqual(recency(1990,2024)["recency_status"],"historical")
        self.assertEqual(recency(None,2024)["recency_status"],"unavailable")

    @pytest.mark.decision("D-005")
    @pytest.mark.test_id("TEST-U-004")
    def test_historical_rank_is_within_same_year_cohort(self):
        rows=[{"metric_id":"x","iso3":"AAA","year":2000,"value":1},{"metric_id":"x","iso3":"BBB","year":2000,"value":2}]
        result=rank_metric_year(rows,COUNTRIES,"x",2000)
        self.assertEqual([(r["iso3"],r["rank"]) for r in result["rows"]],[("BBB",1),("AAA",2)])

    def test_indexed_trajectory(self):
        rows=[{"year":2000,"value":20},{"year":2001,"value":30}]
        self.assertEqual([r["indexed_value"] for r in indexed_trajectory(rows,2000)],[100,150])

    def test_metric_specific_changes(self):
        self.assertAlmostEqual(change_value(121,100,2,"cagr"),10)
        self.assertEqual(change_value(7,5,5,"percentage_point_change"),2)

    @pytest.mark.decision("D-002")
    @pytest.mark.test_id("TEST-F-001")
    def test_country_profile_reports_latest_recency_and_same_year_rank(self):
        rows=[{"metric_id":"x","iso3":"AAA","year":2023,"value":4},{"metric_id":"x","iso3":"BBB","year":2024,"value":5}]
        result=country_profile(rows,COUNTRIES,[{"metric_id":"x"}],"AAA")["metrics"]["x"]
        self.assertEqual(result["latest"]["year"],2023)
        self.assertEqual(result["recency"]["recency_status"],"prior_year")
        self.assertIsNone(result["ranking"]["rank"])


if __name__ == "__main__": unittest.main()
