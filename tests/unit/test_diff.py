import tempfile
import unittest
from pathlib import Path

from gei.diff import snapshot_diff,write_diff


def payload(value=10,countries=("USA",),metric_source="i",release="r1"):
    return {"meta":{"release_id":release,"reference_year":2024},"countries":[{"iso3":c} for c in countries],"metrics":[{"metric_id":"x","source_id":"s","source_dataset_id":"d","source_indicator_id":metric_source}],"observations":[{"iso3":"USA","metric_id":"x","reference_period":"2024","year":2024,"value":value}]}


class DiffTests(unittest.TestCase):
    def test_value_revision_has_absolute_and_percent_change(self):
        diff=snapshot_diff(payload(10),payload(12,release="r2"))
        revision=diff["observations"]["revised"][0]
        self.assertEqual(revision["absolute_change"],2)
        self.assertEqual(revision["percent_change"],20)

    def test_structural_and_source_changes_are_reported(self):
        old=payload();new=payload(countries=("USA","CAN"),metric_source="j",release="r2");new["observations"].append({"iso3":"CAN","metric_id":"x","reference_period":"2025","year":2025,"value":2})
        diff=snapshot_diff(old,new)
        self.assertEqual(diff["countries"]["added"],["CAN"])
        self.assertEqual(len(diff["metrics"]["source_mapping_changes"]),1)
        self.assertEqual(diff["summary"]["observations_added"],1)

    def test_machine_and_human_outputs_are_written(self):
        with tempfile.TemporaryDirectory() as directory:
            paths=write_diff(snapshot_diff(payload(),payload(11,release="r2")),Path(directory),"r1","r2")
            self.assertTrue(all(path.exists() for path in paths))


if __name__=="__main__":unittest.main()
