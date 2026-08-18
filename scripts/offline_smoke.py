import tempfile
from pathlib import Path
from unittest.mock import patch

from gei.fixture import EngineeringFixtureAdapter
from gei.pipeline import build

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    patches=[patch("gei.pipeline.PROCESSED",root/"processed"),patch("gei.pipeline.APP_DATA",root/"app/data"),patch("gei.pipeline.MANIFESTS",root/"manifests"),patch("gei.pipeline.RELEASES",root/"releases"),patch("gei.pipeline.DIFFS",root/"diffs"),patch("gei.pipeline.COUNTRY_REGISTRY_PATH",root/"countries.json")]
    for item in patches:item.start()
    try:
        payload=build(2023,2025,EngineeringFixtureAdapter(),"2000-01-01T00:00:00+00:00")
        assert len(payload["countries"])==50 and len(payload["observations"])==1050
        print(f"Offline analytical smoke build passed: {len(payload['countries'])} synthetic economies, {len(payload['observations'])} observations.")
    finally:
        for item in reversed(patches):item.stop()
