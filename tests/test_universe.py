import unittest

from pipelines.build import normalize, rank_top_economies, select_reference_year


class UniverseTests(unittest.TestCase):
    def test_reference_year_uses_latest_complete_year(self):
        rows = ([{"year": 2023, "value": 1}] * 150 + [{"year": 2024, "value": 1}] * 149)
        self.assertEqual(select_reference_year(rows), 2023)

    def test_gdp_ranking_descending_and_limited(self):
        rows = [
            {"metric_id": "gdp_nominal_usd", "year": 2023, "value": 10, "iso3": "AAA", "country": "A"},
            {"metric_id": "gdp_nominal_usd", "year": 2023, "value": 30, "iso3": "CCC", "country": "C"},
            {"metric_id": "gdp_nominal_usd", "year": 2023, "value": 20, "iso3": "BBB", "country": "B"},
        ]
        ranked = rank_top_economies(rows, 2023, 2)
        self.assertEqual([r["iso3"] for r in ranked], ["CCC", "BBB"])
        self.assertEqual([r["rank"] for r in ranked], [1, 2])

    def test_world_bank_aggregates_are_excluded(self):
        countries = [
            {"id":"WLD","iso2Code":"1W","name":"World","region":{"id":"NA","value":"Aggregates"},"incomeLevel":{"value":"Aggregates"}},
            {"id":"USA","iso2Code":"US","name":"United States","region":{"id":"NAC","value":"North America"},"incomeLevel":{"value":"High income"}},
        ]
        records = {"NY.GDP.MKTP.CD": [
            {"countryiso3code":"WLD","date":"2024","value":100},
            {"countryiso3code":"USA","date":"2024","value":30},
        ]}
        dims, observations = normalize(countries, records)
        self.assertEqual([d["iso3"] for d in dims], ["USA"])
        self.assertEqual([o["iso3"] for o in observations], ["USA"])


if __name__ == "__main__":
    unittest.main()
