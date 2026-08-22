from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).parents[1];source=ROOT/"app";target=ROOT/"dist"
required=[source/"index.html",source/"app.js",source/"styles.css",source/"data/catalog.json"]
missing=[str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:raise SystemExit(f"Static build missing required files: {missing}")
if target.exists():shutil.rmtree(target)
def ignore_static(directory,names):
    path=Path(directory)
    return {"dashboard.json"} if path == source/"data" else set()
shutil.copytree(source,target,ignore=ignore_static)
assets=[]
for path in sorted(target.rglob("*")):
    if path.is_file():assets.append({"path":str(path.relative_to(target)),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={"schema_version":"1.0","release":json.loads((source/"data/catalog.json").read_text())["meta"].get("release_id"),"assets":assets}
(target/"build-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(f"Static build ready: {len(assets)} assets, {sum(row['bytes'] for row in assets):,} bytes")
