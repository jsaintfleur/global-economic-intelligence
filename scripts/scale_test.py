from __future__ import annotations

import argparse
import json
import time
import tracemalloc
from pathlib import Path


def generate(country_count: int, metric_count: int, year_count: int) -> dict:
    countries = [{"iso3": f"C{i:03}", "name": f"Synthetic country {i}"} for i in range(country_count)]
    metrics = [{"metric_id": f"synthetic_{i:03}", "display_name": f"Synthetic metric {i}", "unit": "synthetic units"} for i in range(metric_count)]
    start = 1990
    observations = [{"iso3": country["iso3"], "year": start + y, "reference_period": str(start+y), "metric_id": metric["metric_id"], "value": float((c+1)*(m+1)+y), "source_id": "synthetic_scale_fixture", "source_indicator_id": f"SYN.{m:03}", "retrieved_at": "2000-01-01T00:00:00Z"} for c, country in enumerate(countries) for m, metric in enumerate(metrics) for y in range(year_count)]
    return {"meta":{"synthetic":True},"countries":countries,"metrics":metrics,"observations":observations}


def benchmark(country_count: int, metric_count: int, year_count: int) -> dict:
    tracemalloc.start(); started=time.perf_counter(); payload=generate(country_count,metric_count,year_count); generated=time.perf_counter()
    encoded=json.dumps(payload,separators=(",", ":")).encode(); serialized=time.perf_counter(); _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    return {"countries":country_count,"metrics":metric_count,"years":year_count,"observations":len(payload["observations"]),"json_bytes":len(encoded),"generation_seconds":round(generated-started,3),"serialization_seconds":round(serialized-generated,3),"peak_memory_mb":round(peak/1024/1024,1)}


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=Path("docs/scale-results.json"));args=parser.parse_args()
    results=[benchmark(50,100,30),benchmark(200,100,30)]
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))
