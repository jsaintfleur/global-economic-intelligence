import unittest
from gei.coverage import coverage_matrix


class CoverageTests(unittest.TestCase):
    def test_all_matrix_grains_and_inventory(self):
        observations=[{"iso3":"USA","metric_id":"x","year":2023},{"iso3":"USA","metric_id":"x","year":2024},{"iso3":"CAN","metric_id":"x","year":2024}]
        result=coverage_matrix(observations,[{"iso3":"USA"},{"iso3":"CAN"}],[{"metric_id":"x","display_name":"X","source_id":"s"}],2023,2024)
        self.assertEqual(len(result["country_metric"]),2)
        self.assertEqual(len(result["metric_year"]),2)
        self.assertEqual(result["inventory"][0]["observation_count"],3)


if __name__=="__main__":unittest.main()
