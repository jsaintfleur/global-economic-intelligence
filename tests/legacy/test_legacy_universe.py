"""Compatibility coverage for deprecated, non-production ``pipelines.build``.

This test preserves legacy behavior only. It does not enforce D-002; production
reference-year coverage belongs to ``gei.pipeline`` and its governance-marked tests.
"""
import unittest
from pipelines.build import select_reference_year


class LegacyUniverseTests(unittest.TestCase):
    def test_legacy_reference_year_contract(self):
        rows=([{"year":2023,"value":1}]*150+[{"year":2024,"value":1}]*149)
        self.assertEqual(select_reference_year(rows),2023)


if __name__ == "__main__": unittest.main()
