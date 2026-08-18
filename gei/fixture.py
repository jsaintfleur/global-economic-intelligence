from __future__ import annotations

from gei.adapters import AdapterResult,SourceAdapter
from gei.schemas import RawSnapshot


def _iso3(index:int)->str:return chr(65+(index//676)%26)+chr(65+(index//26)%26)+chr(65+index%26)


class EngineeringFixtureAdapter(SourceAdapter):
    """Deterministic, explicitly synthetic adapter for offline smoke builds."""
    source_id="world_bank_wdi";source_dataset_id="world_development_indicators"
    def _result(self,indicator,records):return AdapterResult(records,RawSnapshot(f"raw_fixture_{indicator}",self.source_id,self.source_dataset_id,indicator,"2000-01-01T00:00:00Z",f"fixture/{indicator}.json",len(records),"0"*64,"engineering-fixture-v1"),[],[])
    def fetch_countries(self,retrieved_at):
        rows=[{"id":_iso3(i),"iso2Code":chr(65+(i//26)%26)+chr(65+i%26),"name":f"Synthetic economy {i:03}","region":{"id":"FIX","value":"Synthetic region"},"incomeLevel":{"value":"Synthetic group"}} for i in range(150)]
        return self._result("countries",rows)
    def fetch_indicator(self,indicator_id,start,end,retrieved_at):
        rows=[{"countryiso3code":_iso3(i),"date":str(year),"value":float((i+1)*100+(year-start))} for year in range(start,end+1) for i in range(150)]
        return self._result(indicator_id,rows)
