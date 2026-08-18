"""Compatibility coverage for the non-production pipelines.build module."""
import unittest
from pipelines.build import select_reference_year


class LegacyUniverseTests(unittest.TestCase):
    def test_legacy_reference_year_contract(self):
        rows=([{"year":2023,"value":1}]*150+[{"year":2024,"value":1}]*149)
        self.assertEqual(select_reference_year(rows),2023)


if __name__ == "__main__": unittest.main()
