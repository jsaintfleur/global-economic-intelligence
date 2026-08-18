import argparse
import csv
import json
from pathlib import Path


parser=argparse.ArgumentParser();parser.add_argument("--input",type=Path,default=Path("data/processed/coverage.json"));parser.add_argument("--csv",type=Path);args=parser.parse_args()
rows=json.loads(args.input.read_text())["inventory"]
if args.csv:
    with args.csv.open("w",newline="",encoding="utf-8") as handle:writer=csv.DictWriter(handle,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
print(f"{'Metric':32} {'Source':18} {'Countries':>9} {'Years':>11} {'Obs':>7} {'Missing':>8}")
for row in rows:print(f"{row['metric_id'][:32]:32} {row['source_id'][:18]:18} {row['country_count']:9} {row['earliest_year']}-{row['latest_year']} {row['observation_count']:7} {row['missing_country_count']:8}")
