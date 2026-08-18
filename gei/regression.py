from __future__ import annotations

from collections import Counter


def evaluate_regressions(old: dict | None, new: dict, diff: dict | None, rules: list[dict], shard_ids: set[str]) -> dict:
    config={rule["rule_id"]:rule for rule in rules};findings=[]
    def add(rule_id,message,actual):
        rule=config[rule_id];findings.append({"rule_id":rule_id,"severity":rule["severity"],"blocking":rule["blocking"],"message":message,"actual":actual,"threshold":rule["threshold"]})
    required=("source_id","source_dataset_id","source_indicator_id","raw_snapshot_id","pipeline_run_id")
    missing=sum(any(not row.get(field) for field in required) for row in new.get("observations",[]))
    if missing>config["provenance_missing"]["threshold"]["count"]:add("provenance_missing","Observations have missing provenance",missing)
    keys=[(r.get("iso3"),r.get("metric_id"),r.get("reference_period",r.get("year"))) for r in new.get("observations",[])];duplicates=sum(count-1 for count in Counter(keys).values() if count>1)
    if duplicates>0:add("duplicate_keys","Duplicate canonical observation keys detected",duplicates)
    expected={m["metric_id"] for m in new.get("metrics",[])};missing_shards=sorted(expected-shard_ids)
    if missing_shards:add("metric_shard_missing","Metric shards are missing",missing_shards)
    if old and diff:
        old_count=diff["summary"]["old_observation_count"];new_count=diff["summary"]["new_observation_count"];drop=0 if old_count==0 else (old_count-new_count)/old_count*100
        if drop>config["observation_count_drop"]["threshold"]["percent"]:add("observation_count_drop","Observation count decreased",drop)
        if len(diff["countries"]["removed"])>config["country_removed"]["threshold"]["count"]:add("country_removed","Countries disappeared",diff["countries"]["removed"])
        if len(diff["metrics"]["removed"])>config["metric_removed"]["threshold"]["count"]:add("metric_removed","Metrics disappeared",diff["metrics"]["removed"])
        if diff["metrics"]["source_mapping_changes"]:add("source_mapping_changed","Source mappings changed",diff["metrics"]["source_mapping_changes"])
        regressed=[row for row in diff["latest_year_changes"] if row["old_latest_year"] is not None and row["new_latest_year"] is not None and row["new_latest_year"]<row["old_latest_year"]]
        if regressed:add("latest_year_regressed","Latest available year regressed",regressed)
    return {"schema_version":"1.0","status":"failed" if any(f["blocking"] for f in findings) else "passed","blocking_findings":sum(f["blocking"] for f in findings),"findings":findings}
