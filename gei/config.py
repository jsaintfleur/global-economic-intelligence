import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
MANIFESTS = DATA / "manifests"
DIFFS = DATA / "diffs"
RELEASES = DATA / "releases"
APP_DATA = ROOT / "app" / "data"
METRIC_REGISTRY_PATH = ROOT / "config" / "metrics.json"
REGRESSION_RULES_PATH = ROOT / "config" / "regression_rules.json"

WORLD_BANK_BASE = "https://api.worldbank.org/v2"
START_YEAR = 1990
END_YEAR = 2025
TOP_N = 50


def load_metric_registry(path: Path = METRIC_REGISTRY_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0" or not isinstance(payload.get("metrics"), list):
        raise ValueError("Unsupported or malformed metric registry")
    return payload["metrics"]


def metrics_by_id() -> dict[str, dict]:
    return {metric["metric_id"]: metric for metric in load_metric_registry()}
