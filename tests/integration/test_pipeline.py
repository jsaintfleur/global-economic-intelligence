import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gei.adapters import AdapterResult, SourceAdapter
from gei.pipeline import build
from gei.universe import select_universe
from gei.schemas import RawSnapshot


def iso3(index):
    return chr(65+(index//676)%26)+chr(65+(index//26)%26)+chr(65+index%26)


class FixtureAdapter(SourceAdapter):
    source_id="world_bank_wdi"; source_dataset_id="world_development_indicators"
    def __init__(self): self.calls=0
    def _result(self, indicator, records):
        self.calls+=1
        snap=RawSnapshot(f"raw_{indicator}",self.source_id,self.source_dataset_id,indicator,"2026-01-01",f"raw/{indicator}.json",len(records),"0"*64)
        return AdapterResult(records,snap,[],[])
    def fetch_countries(self,retrieved_at):
        rows=[{"id":iso3(i),"iso2Code":chr(65+(i//26)%26)+chr(65+i%26),"name":f"Country {i}","region":{"id":"R","value":"Region"},"incomeLevel":{"value":"Income"}} for i in range(150)]
        return self._result("countries",rows)
    def fetch_indicator(self,indicator_id,start,end,retrieved_at):
        rows=[{"countryiso3code":iso3(i),"date":str(year),"value":float(1000-i if indicator_id=="NY.GDP.MKTP.CD" else i+year)} for year in range(start,end+1) for i in range(150)]
        return self._result(indicator_id,rows)


class PipelineIntegrationTests(unittest.TestCase):
    def test_pipeline_is_deterministic_from_identical_inputs_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); processed=root/"processed"; app=root/"app"; manifests=root/"manifests"
            entity_path=root/"entities.json"; entity_path.write_text(json.dumps({"schema_version":"1.0","eligibility_policy_version":"test","entities":[{"analytical_entity_id":f"entity:{iso3(i)}","display_name":f"Country {i}","analytical_eligibility":"included" if i<50 else "pending_review","eligibility_policy_version":"test","eligibility_basis":"fixture","effective_from":"2026-01-01","effective_to":None,"review_owner":"tests","authoritative_ids":{"world_bank_code":iso3(i),"imf_weo_code":None,"iso3":iso3(i),"un_m49":None},"source_references":["fixture"]} for i in range(150)]}))
            patches=(patch("gei.pipeline.PROCESSED",processed),patch("gei.pipeline.APP_DATA",app),patch("gei.pipeline.MANIFESTS",manifests),patch("gei.pipeline.RELEASES",root/"releases"),patch("gei.pipeline.DIFFS",root/"diffs"),patch("gei.pipeline.COUNTRY_REGISTRY_PATH",root/"countries.json"),patch("gei.pipeline.ANALYTICAL_ENTITY_REGISTRY_PATH",entity_path))
            for item in patches:item.start()
            try:
                first=build(2024,2025,FixtureAdapter(),"2026-01-01T00:00:00+00:00")
                first_bytes=(processed/"dashboard.json").read_bytes()
                second=build(2024,2025,FixtureAdapter(),"2026-01-01T00:00:00+00:00")
                self.assertEqual(first_bytes,(processed/"dashboard.json").read_bytes())
                self.assertEqual(len(first["countries"]),50)
                self.assertEqual(len(list(manifests.glob("*.json"))),1)
                self.assertEqual(first["meta"]["pipeline_run_id"],second["meta"]["pipeline_run_id"])
                self.assertIs(select_universe,__import__("gei.pipeline",fromlist=["select_universe"]).select_universe)
            finally:
                for item in reversed(patches):item.stop()


if __name__ == "__main__": unittest.main()
