"""Compatibility entry point; the canonical implementation is gei.pipeline."""

from __future__ import annotations

from collections import Counter

from gei.pipeline import build, _normalize_countries, _normalize_observations
from gei.config import load_metric_registry


def select_reference_year(rows: list[dict], minimum_countries: int = 150) -> int:
    counts = Counter(int(row["year"]) for row in rows if row.get("value") is not None)
    eligible = [year for year, count in counts.items() if count >= minimum_countries]
    if not eligible:
        raise ValueError("No GDP year meets the completeness threshold")
    return max(eligible)


def rank_top_economies(rows: list[dict], reference_year: int, limit: int = 50) -> list[dict]:
    accepted_ids = {"gdp_current_usd", "gdp_nominal_usd"}
    ranked = sorted((row for row in rows if row["metric_id"] in accepted_ids and row["year"] == reference_year and row["value"] is not None), key=lambda row: (-row["value"], row["iso3"]))[:limit]
    return [{"iso3": row["iso3"], "country": row.get("country", row.get("name")), "gdp": row["value"], "reference_year": reference_year, "rank": index + 1} for index, row in enumerate(ranked)]


def normalize(countries: list[dict], raw: dict[str, list[dict]]) -> tuple[list[dict], list[dict]]:
    dims = _normalize_countries(countries)
    registry = {metric["source_indicator_id"]: metric for metric in load_metric_registry()}
    observations = []
    for indicator, rows in raw.items():
        normalized, _ = _normalize_observations(rows, registry[indicator], dims, "legacy_raw", "legacy_run", "legacy")
        observations.extend({**row, "country": dims[row["iso3"]]["name"]} for row in normalized)
    return list(dims.values()), observations


if __name__ == "__main__":
    result = build()
    print(f"Built {len(result['observations']):,} observations.")
