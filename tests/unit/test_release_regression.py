import unittest
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from gei.regression import evaluate_regressions
from gei.release import build_release
from gei.pipeline import _write_vintage_store


RULES=[{"rule_id":key,"severity":"error" if key in {"provenance_missing","duplicate_keys","metric_shard_missing","metric_removed"} else "warning","blocking":key in {"provenance_missing","duplicate_keys","metric_shard_missing","metric_removed"},"threshold":{"count":0,"percent":5,"years":0}} for key in ["observation_count_drop","country_removed","metric_removed","source_mapping_changed","latest_year_regressed","provenance_missing","duplicate_keys","metric_shard_missing","file_size_change"]]


class ReleaseRegressionTests(unittest.TestCase):
    def test_release_id_is_content_deterministic(self):
        payload={"meta":{"pipeline_run_id":"run","generated_at":"now"},"observations":[{"observation_id":"o","value":1,"year":2024}],"countries":[{}],"metrics":[{}]}
        args=(payload,["raw"],None,{"metric_registry":"m","country_registry":"c","source_registry":"s","transformation_registry":"t"},{"a":"1"},[])
        self.assertEqual(build_release(*args)["release_id"],build_release(*args)["release_id"])

    @pytest.mark.decision("D-006")
    @pytest.mark.test_id("TEST-T-001")
    @pytest.mark.test_id("TEST-T-002")
    def test_vintage_store_is_append_only_and_collision_safe(self):
        payload={"meta":{"release_id":"release_test"},"observations":[{"observation_id":"o","source_vintage":"2026-01-01"}]}
        with tempfile.TemporaryDirectory() as directory, patch("gei.pipeline.PROCESSED",Path(directory)):
            path=_write_vintage_store(payload)
            self.assertEqual(path.read_text(), '[{"observation_id":"o","source_vintage":"2026-01-01"}]')
            _write_vintage_store(payload)
            with self.assertRaisesRegex(ValueError,"append-only vintage collision"):
                _write_vintage_store({**payload,"observations":[{"observation_id":"changed","source_vintage":"2026-01-01"}]})

    def test_missing_provenance_is_blocking(self):
        new={"metrics":[{"metric_id":"x"}],"observations":[{"iso3":"USA","metric_id":"x","year":2024}]}
        report=evaluate_regressions(None,new,None,RULES,{"x"})
        self.assertEqual(report["status"],"failed")

    def test_value_revisions_do_not_block(self):
        complete={"iso3":"USA","metric_id":"x","reference_period":"2024","source_id":"s","source_dataset_id":"d","source_indicator_id":"i","raw_snapshot_id":"r","pipeline_run_id":"p"}
        new={"metrics":[{"metric_id":"x"}],"observations":[complete]}
        report=evaluate_regressions(new,new,{"summary":{"old_observation_count":1,"new_observation_count":1},"countries":{"removed":[]},"metrics":{"removed":[],"source_mapping_changes":[]},"latest_year_changes":[]},RULES,{"x"})
        self.assertEqual(report["status"],"passed")


if __name__=="__main__":unittest.main()
