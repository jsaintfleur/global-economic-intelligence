import unittest
import pytest

from gei.universe import NormalizedGDPProvider, select_universe


def entity(iso3, eligibility="included"):
    return {"analytical_entity_id":f"entity:{iso3}","iso3":iso3,"name":iso3,"analytical_eligibility":eligibility,"eligibility_policy_version":"test"}


class ProductionUniverseTests(unittest.TestCase):
    def test_latest_complete_year_uses_production_function(self):
        entities={f"A{i:02}":entity(f"A{i:02}") for i in range(3)}
        rows=[{"country_id":f"country:{iso}","iso3":iso,"year":2024,"value":10-i,"source_id":"source","source_indicator_id":"gdp"} for i,iso in enumerate(entities)]
        rows += [{"country_id":"country:A00","iso3":"A00","year":2025,"value":11,"source_id":"source","source_indicator_id":"gdp"}]
        year,universe,_=select_universe(NormalizedGDPProvider(rows),entities,top_n=3,minimum_observations=3)
        self.assertEqual(year,2024);self.assertEqual(len(universe),3)

    def test_ties_use_iso3_and_nonincluded_entities_are_excluded(self):
        entities={"BBB":entity("BBB"),"AAA":entity("AAA"),"CCC":entity("CCC","pending_review")}
        rows=[{"country_id":f"country:{iso}","iso3":iso,"year":2025,"value":10,"source_id":"source","source_indicator_id":"gdp"} for iso in entities]
        year,universe,excluded=select_universe(NormalizedGDPProvider(rows),entities,top_n=2,minimum_observations=2)
        self.assertEqual(year,2025);self.assertEqual([row["iso3"] for row in universe],["AAA","BBB"]);self.assertEqual(universe[0]["gdp_rank"],1)
        self.assertEqual(excluded[0]["iso3"],"CCC")

    def test_exact_top_n_selection(self):
        entities={f"A{i:02}":entity(f"A{i:02}") for i in range(60)}
        rows=[{"country_id":f"country:{iso}","iso3":iso,"year":2025,"value":100-i,"source_id":"source","source_indicator_id":"gdp"} for i,iso in enumerate(entities)]
        _,universe,_=select_universe(NormalizedGDPProvider(rows),entities,top_n=50,minimum_observations=50)
        self.assertEqual(len(universe),50)


if __name__ == "__main__": unittest.main()
