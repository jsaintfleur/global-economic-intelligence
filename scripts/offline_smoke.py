import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from gei.fixture import EngineeringFixtureAdapter, _iso3
from gei.pipeline import build

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    entity_path=root/"analytical_entities.json"
    entity_path.write_text(json.dumps({"schema_version":"1.0","eligibility_policy_version":"fixture_v1","authority":"engineering fixture only","entities":[{"analytical_entity_id":f"entity:{_iso3(i)}","display_name":f"Synthetic economy {i:03}","analytical_eligibility":"included","eligibility_policy_version":"fixture_v1","eligibility_basis":"deterministic engineering fixture","authoritative_ids":{"world_bank_code":_iso3(i),"iso3":_iso3(i),"un_m49":None,"imf_weo_code":None},"source_references":["engineering fixture"],"effective_from":"2000-01-01","effective_to":None,"review_owner":"engineering"} for i in range(50)]}))
    patches=[patch("gei.pipeline.PROCESSED",root/"processed"),patch("gei.pipeline.APP_DATA",root/"app/data"),patch("gei.pipeline.MANIFESTS",root/"manifests"),patch("gei.pipeline.RELEASES",root/"releases"),patch("gei.pipeline.DIFFS",root/"diffs"),patch("gei.pipeline.COUNTRY_REGISTRY_PATH",root/"countries.json"),patch("gei.pipeline.ANALYTICAL_ENTITY_REGISTRY_PATH",entity_path)]
    for item in patches:item.start()
    try:
        payload=build(2023,2025,EngineeringFixtureAdapter(),"2000-01-01T00:00:00+00:00")
        assert len(payload["countries"])==50 and len(payload["observations"])==1050
        print(f"Offline analytical smoke build passed: {len(payload['countries'])} synthetic economies, {len(payload['observations'])} observations.")
    finally:
        for item in reversed(patches):item.stop()
