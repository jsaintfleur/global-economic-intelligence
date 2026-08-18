import math
from collections import defaultdict
from typing import Iterable, Optional


def pct_change(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous in (None, 0):
        return None
    return (current / previous - 1) * 100


def cagr(end: Optional[float], start: Optional[float], years: int) -> Optional[float]:
    if end is None or start is None or start <= 0 or end < 0 or years <= 0:
        return None
    return ((end / start) ** (1 / years) - 1) * 100


def rank_desc(values: dict[str, Optional[float]]) -> dict[str, Optional[int]]:
    valid = sorted(((key, value) for key, value in values.items() if value is not None), key=lambda x: (-x[1], x[0]))
    return {**{key: None for key in values}, **{key: index + 1 for index, (key, _) in enumerate(valid)}}


def latest_by_country(rows: Iterable[dict], metric_id: str) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for row in rows:
        if row["metric_id"] != metric_id or row["value"] is None:
            continue
        current = latest.get(row["iso3"])
        if current is None or row["year"] > current["year"]:
            latest[row["iso3"]] = row
    return latest


def choose_reference_year(rows: Iterable[dict], metric_id: str, min_count: int = 150, coverage: float = 0.90) -> int:
    by_year: dict[int, set[str]] = defaultdict(set)
    for row in rows:
        if row["metric_id"] == metric_id and row["value"] is not None:
            by_year[row["year"]].add(row["iso3"])
    eligible = [year for year, countries in by_year.items() if len(countries) >= math.ceil(min_count * coverage)]
    if not eligible:
        raise ValueError("No sufficiently complete reference year")
    return max(eligible)


def rebase(series: list[dict], base_year: int) -> list[dict]:
    base = next((row["value"] for row in series if row["year"] == base_year), None)
    return [{**row, "rebased_value": None if base in (None, 0) or row["value"] is None else row["value"] / base * 100} for row in series]

