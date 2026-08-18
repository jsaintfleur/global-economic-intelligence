import unittest
from gei.fixture import EngineeringFixtureAdapter


class SourceAdapterContractTests(unittest.TestCase):
    def test_identity_and_snapshot_contract(self):
        adapter=EngineeringFixtureAdapter();result=adapter.fetch_indicator("TEST",2024,2024,"now")
        self.assertTrue(adapter.source_id and adapter.source_dataset_id)
        self.assertGreater(len(result.records),0)
        self.assertEqual(result.snapshot.source_id,adapter.source_id)
        self.assertTrue(result.snapshot.raw_snapshot_id)
        self.assertEqual(result.snapshot.record_count,len(result.records))

    def test_country_ingest_contract(self):
        result=EngineeringFixtureAdapter().fetch_countries("now")
        self.assertTrue(all(row.get("id") for row in result.records))
        self.assertEqual(result.rejected,[])


if __name__=="__main__":unittest.main()
