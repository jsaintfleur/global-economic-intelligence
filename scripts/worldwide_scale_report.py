"""Measure the committed worldwide foundation without constructing a monolithic browser payload."""
import json
import time
import tracemalloc
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    started = time.perf_counter()
    value = json.loads(path.read_text())
    return value, round((time.perf_counter() - started) * 1000, 2)


def main() -> None:
    tracemalloc.start()
    payload_path = ROOT / "data/processed/dashboard.json"
    payload, payload_ms = load(payload_path)
    _, peak = tracemalloc.get_traced_memory()
    catalog_path = ROOT / "app/data/catalog.json"
    catalog, catalog_ms = load(catalog_path)
    metric_files = sorted((ROOT / "app/data/metrics").glob("*.json"))
    profile_files = sorted((ROOT / "app/data/profiles").glob("*.json"))
    ranking_files = sorted((ROOT / "app/data/rankings").glob("*.json"))
    worldwide_files = sorted((ROOT / "app/data/rankings_worldwide").glob("*.json"))
    report = {
        "release_id": payload["meta"]["release_id"],
        "ingested_entities": len(payload["ingestion_entities"]),
        "materialized_top50": len(payload["countries"]),
        "observations": len(payload["observations"]),
        "canonical_store_bytes": payload_path.stat().st_size,
        "canonical_load_ms": payload_ms,
        "catalog_bytes": catalog_path.stat().st_size,
        "catalog_load_ms": catalog_ms,
        "metric_shards": {"count": len(metric_files), "bytes": sum(p.stat().st_size for p in metric_files), "max_bytes": max(p.stat().st_size for p in metric_files)},
        "profile_shards": {"count": len(profile_files), "bytes": sum(p.stat().st_size for p in profile_files), "max_bytes": max(p.stat().st_size for p in profile_files)},
        "top50_ranking_shards": {"count": len(ranking_files), "bytes": sum(p.stat().st_size for p in ranking_files), "max_bytes": max(p.stat().st_size for p in ranking_files)},
        "worldwide_ranking_shards": {"count": len(worldwide_files), "bytes": sum(p.stat().st_size for p in worldwide_files), "max_bytes": max(p.stat().st_size for p in worldwide_files)},
        "peak_measurement_memory_mb": round(peak / 1024 / 1024, 2),
        "browser_initial_payload_bytes": catalog_path.stat().st_size,
        "browser_compatibility_payload_bytes": (ROOT / "app/data/dashboard.json").stat().st_size,
        "browser_compatibility_payload_deployed": False,
        "architecture": "catalog plus lazy metric/profile/ranking shards; canonical worldwide store is not an initial browser payload",
    }
    target = ROOT / "docs/audit/WORLDWIDE_SCALE.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
