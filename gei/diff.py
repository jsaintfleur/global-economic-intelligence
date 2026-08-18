from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional


def snapshot_diff(old: dict, new: dict, material_abs: float = 0.0, material_pct: float = 0.0) -> dict:
    old_obs={_key(row):row for row in old.get("observations",[])};new_obs={_key(row):row for row in new.get("observations",[])}
    added=sorted(new_obs.keys()-old_obs.keys());removed=sorted(old_obs.keys()-new_obs.keys());revisions=[]
    for key in sorted(old_obs.keys()&new_obs.keys()):
        before,after=old_obs[key].get("value"),new_obs[key].get("value")
        if before==after:continue
        absolute=None if before is None or after is None else after-before
        percent=None if absolute is None or before==0 else absolute/abs(before)*100
        material=(absolute is not None and abs(absolute)>=material_abs) and (percent is None or abs(percent)>=material_pct)
        revisions.append({"key":list(key),"old_value":before,"new_value":after,"absolute_change":absolute,"percent_change":percent,"material":material})
    old_c={c["iso3"] for c in old.get("countries",[])};new_c={c["iso3"] for c in new.get("countries",[])}
    old_m={m["metric_id"]:m for m in old.get("metrics",[])};new_m={m["metric_id"]:m for m in new.get("metrics",[])}
    source_changes=[]
    for metric_id in sorted(old_m.keys()&new_m.keys()):
        fields=("source_id","source_dataset_id","source_indicator_id")
        before={field:old_m[metric_id].get(field) for field in fields};after={field:new_m[metric_id].get(field) for field in fields}
        if before!=after:source_changes.append({"metric_id":metric_id,"old":before,"new":after})
    old_latest=_latest(old_obs.values());new_latest=_latest(new_obs.values())
    latest_changes=[{"iso3":key[0],"metric_id":key[1],"old_latest_year":old_latest.get(key),"new_latest_year":new_latest.get(key)} for key in sorted(set(old_latest)|set(new_latest)) if old_latest.get(key)!=new_latest.get(key)]
    return {"schema_version":"1.0","old_release_id":old.get("meta",{}).get("release_id"),"new_release_id":new.get("meta",{}).get("release_id"),"summary":{"old_observation_count":len(old_obs),"new_observation_count":len(new_obs),"observations_added":len(added),"observations_removed":len(removed),"observations_revised":len(revisions),"material_revisions":sum(r["material"] for r in revisions)},"observations":{"added":[list(k) for k in added],"removed":[list(k) for k in removed],"revised":revisions},"countries":{"added":sorted(new_c-old_c),"removed":sorted(old_c-new_c)},"metrics":{"added":sorted(new_m.keys()-old_m.keys()),"removed":sorted(old_m.keys()-new_m.keys()),"source_mapping_changes":source_changes},"reference_year":{"old":old.get("meta",{}).get("reference_year"),"new":new.get("meta",{}).get("reference_year")},"latest_year_changes":latest_changes,"coverage_changes":_coverage_changes(old_obs.values(),new_obs.values())}


def write_diff(diff: dict, directory: Path, old_id: str, new_id: str) -> tuple[Path,Path]:
    directory.mkdir(parents=True,exist_ok=True);stem=f"{old_id}__{new_id}";json_path=directory/f"{stem}.json";md_path=directory/f"{stem}.md"
    json_path.write_text(json.dumps(diff,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    s=diff["summary"];md_path.write_text(f"# Dataset diff: {old_id} → {new_id}\n\n- Observations: {s['old_observation_count']:,} → {s['new_observation_count']:,}\n- Added: {s['observations_added']:,}\n- Removed: {s['observations_removed']:,}\n- Revised: {s['observations_revised']:,}\n- Material under configured thresholds: {s['material_revisions']:,}\n- Countries added/removed: {len(diff['countries']['added'])}/{len(diff['countries']['removed'])}\n- Metrics added/removed: {len(diff['metrics']['added'])}/{len(diff['metrics']['removed'])}\n- Source mapping changes: {len(diff['metrics']['source_mapping_changes'])}\n- Reference year: {diff['reference_year']['old']} → {diff['reference_year']['new']}\n",encoding="utf-8")
    return json_path,md_path


def _key(row):return(row.get("iso3"),row.get("metric_id"),row.get("reference_period",str(row.get("year"))))
def _latest(rows):
    result={}
    for row in rows:
        key=(row.get("iso3"),row.get("metric_id"));result[key]=max(result.get(key,-10**9),row.get("year",-10**9))
    return result
def _coverage_changes(old_rows,new_rows):
    def counts(rows):return Counter((r.get("iso3"),r.get("metric_id")) for r in rows)
    old,new=counts(old_rows),counts(new_rows)
    return [{"iso3":key[0],"metric_id":key[1],"old_count":old.get(key,0),"new_count":new.get(key,0),"change":new.get(key,0)-old.get(key,0)} for key in sorted(set(old)|set(new)) if old.get(key,0)!=new.get(key,0)]
