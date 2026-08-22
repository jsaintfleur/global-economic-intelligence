import unittest
import pytest

from gei.pipeline import _normalize_countries, _normalize_observations


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.countries = _normalize_countries([
            {"id":"USA","iso2Code":"US","name":"United States","region":{"id":"NAC","value":"North America"},"incomeLevel":{"value":"High income"}},
            {"id":"WLD","iso2Code":"1W","name":"World","region":{"id":"NA","value":"Aggregates"},"incomeLevel":{"value":"Aggregates"}},
        ])
        self.metric = {"metric_id":"x","source_id":"s","source_dataset_id":"d","source_indicator_id":"i","unit":"u","frequency":"annual","transformation":"identity"}

    @pytest.mark.decision("D-003")
    @pytest.mark.test_id("TEST-U-001")
    def test_country_normalization_excludes_aggregates(self):
        self.assertEqual(list(self.countries), ["USA"])

    @pytest.mark.decision("D-006")
    @pytest.mark.test_id("TEST-T-002")
    def test_provenance_propagates_and_ids_are_stable(self):
        rows = [{"countryiso3code":"USA","date":"2024","value":2}]
        first, _ = _normalize_observations(rows,self.metric,self.countries,"raw_1","run_1","2026-01-01")
        second, _ = _normalize_observations(rows,self.metric,self.countries,"raw_1","run_2","2026-01-02")
        self.assertEqual(first[0]["observation_id"], second[0]["observation_id"])
        self.assertEqual(first[0]["raw_snapshot_id"], "raw_1")
        self.assertEqual(first[0]["pipeline_run_id"], "run_1")

    def test_malformed_partial_and_duplicate_records_are_rejected(self):
        rows = [
            {"countryiso3code":"USA","date":"2024","value":2},
            {"countryiso3code":"USA","date":"2024","value":3},
            {"countryiso3code":"USA","date":"bad","value":3},
            {"countryiso3code":"ZZZ","date":"2024","value":3},
            {"countryiso3code":"USA","date":"2023","value":None},
        ]
        accepted, rejected = _normalize_observations(rows,self.metric,self.countries,"raw","run","now")
        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(rejected), 4)


if __name__ == "__main__": unittest.main()
