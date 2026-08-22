import unittest

from gei.config import load_metric_registry
from gei.validation import REQUIRED_METRIC_FIELDS, validate_metric_registry


class MetricRegistryTests(unittest.TestCase):
    def setUp(self):
        self.metrics = load_metric_registry()

    def test_registry_is_structurally_valid(self):
        self.assertTrue(validate_metric_registry(self.metrics).valid)

    def test_metric_ids_are_unique(self):
        ids = [m["metric_id"] for m in self.metrics]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_metric_has_canonical_fields(self):
        self.assertTrue(all(REQUIRED_METRIC_FIELDS <= metric.keys() for metric in self.metrics))

    def test_debt_definition_is_general_government_with_new_identity(self):
        debt = next(m for m in self.metrics if m["metric_id"] == "general_government_gross_debt_pct_gdp")
        self.assertIn("General government", debt["display_name"])
        self.assertEqual(debt["source_id"], "imf_weo")
        self.assertEqual(debt["source_indicator_id"], "GGXWDG_NGDP")
        self.assertNotIn("central_government_debt_pct_gdp", {m["metric_id"] for m in self.metrics})


if __name__ == "__main__":
    unittest.main()
