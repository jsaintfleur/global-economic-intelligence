import argparse
import json
from pathlib import Path

from gei.diff import snapshot_diff,write_diff

parser=argparse.ArgumentParser();parser.add_argument("old",type=Path);parser.add_argument("new",type=Path);parser.add_argument("--output",type=Path,default=Path("data/diffs"));parser.add_argument("--material-abs",type=float,default=0);parser.add_argument("--material-pct",type=float,default=0);args=parser.parse_args()
old=json.loads(args.old.read_text());new=json.loads(args.new.read_text());diff=snapshot_diff(old,new,args.material_abs,args.material_pct);old_id=old.get("meta",{}).get("release_id",args.old.stem);new_id=new.get("meta",{}).get("release_id",args.new.stem);paths=write_diff(diff,args.output,old_id,new_id);print("\n".join(map(str,paths)))
