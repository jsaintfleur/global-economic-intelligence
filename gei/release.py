from __future__ import annotations

import hashlib
import json
from pathlib import Path


def content_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


def build_release(payload: dict, raw_snapshot_ids: list[str], code_commit: str | None, registry_versions: dict, adapter_versions: dict, warnings: list[str]) -> dict:
    observations=payload["observations"]
    material={"registry_versions":registry_versions,"raw_snapshot_ids":sorted(raw_snapshot_ids),"observation_digest":content_hash([(r["observation_id"],r["value"]) for r in observations])}
    release_id=f"release_{content_hash(material)[:20]}"
    years=[row["year"] for row in observations]
    return {"schema_version":"1.1","release_id":release_id,"generated_at":payload["meta"]["generated_at"],"pipeline_run_id":payload["meta"]["pipeline_run_id"],"code_commit":code_commit,"metric_registry_version":registry_versions["metric_registry"],"country_registry_version":registry_versions["country_registry"],"analytical_entity_registry_version":registry_versions.get("analytical_entity_registry"),"source_registry_version":registry_versions["source_registry"],"transformation_registry_version":registry_versions["transformation_registry"],"source_adapter_versions":adapter_versions,"raw_snapshot_ids":raw_snapshot_ids,"observation_count":len(observations),"country_count":len(payload["countries"]),"metric_count":len(payload["metrics"]),"year_range":{"start":min(years),"end":max(years)},"validation_status":"passed","warnings":warnings,"asset_version":content_hash(material)[:16]}


def write_release(release: dict, payload: dict, root: Path) -> tuple[Path,Path]:
    root.mkdir(parents=True,exist_ok=True);snapshots=root/"snapshots";snapshots.mkdir(exist_ok=True)
    release_path=root/f"{release['release_id']}.json";release_path.write_text(json.dumps(release,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    snapshot_path=snapshots/f"{release['release_id']}.json";snapshot_path.write_text(json.dumps(payload,separators=(",", ":"),sort_keys=True),encoding="utf-8")
    (root/"latest.json").write_text(json.dumps(release,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return release_path,snapshot_path
