import unittest
import pytest

from gei.validation import validate_metric_registry, validate_observations


class ValidationTests(unittest.TestCase):
    def test_duplicate_metric_ids_are_rejected(self):
        base = {"metric_id":"x","display_name":"X","source_id":"s","source_dataset_id":"d","source_indicator_id":"i","unit":"u","frequency":"annual","value_type":"level","formatting":"number","transformation":"identity","missing_data_policy":"preserve_missing"}
        report = validate_metric_registry([base, dict(base)])
        self.assertFalse(report.valid)
        self.assertIn("duplicate metric IDs", report.errors[0])

    @pytest.mark.decision("D-006")
    @pytest.mark.test_id("TEST-T-001")
    def test_duplicate_observation_key_is_rejected(self):
        row = {"observation_id":"obs_1","country_id":"country:USA","iso3":"USA","reference_period":"2024","year":2024,"metric_id":"x","value":1.0,"unit":"u","frequency":"annual","source_id":"s","source_dataset_id":"d","source_indicator_id":"i","retrieved_at":"2026-01-01T00:00:00Z","raw_snapshot_id":"raw_1","raw_record_index":0,"transformation_id":"identity","pipeline_run_id":"run_1"}
        other = {**row,"observation_id":"obs_2","raw_record_index":1}
        report = validate_observations([row, other], [{"iso3":"USA"}], [{"metric_id":"x"}])
        self.assertFalse(report.valid)
        self.assertTrue(any("duplicate observation key" in error for error in report.errors))

    @pytest.mark.decision("D-003")
    @pytest.mark.test_id("TEST-E-002")
    def test_orphan_and_invalid_iso_are_rejected(self):
        row = {"observation_id":"obs_1","country_id":"country:xx","iso3":"xx","reference_period":"2024","year":2024,"metric_id":"missing","value":1.0,"unit":"u","frequency":"annual","source_id":"s","source_dataset_id":"d","source_indicator_id":"i","retrieved_at":"x","raw_snapshot_id":"raw","raw_record_index":0,"transformation_id":"identity","pipeline_run_id":"run"}
        report = validate_observations([row], [{"iso3":"USA"}], [{"metric_id":"x"}])
        self.assertGreaterEqual(len(report.errors), 3)


if __name__ == "__main__": unittest.main()
