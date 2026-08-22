from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Iterable, Optional


RECENCY_STATUSES = {"current_year", "prior_year", "historical", "unavailable"}


def _analytical_observation(row: dict) -> bool:
    return row.get("observation_class") in (None, "actual", "estimate")


def recency(latest_year: Optional[int], metric_max_year: Optional[int]) -> dict:
    if latest_year is None or metric_max_year is None:
        return {"latest_observation_year": latest_year, "metric_max_year": metric_max_year, "lag_years": None, "recency_status": "unavailable"}
    lag = metric_max_year - latest_year
    status = "current_year" if lag == 0 else "prior_year" if lag == 1 else "historical"
    return {"latest_observation_year": latest_year, "metric_max_year": metric_max_year, "lag_years": lag, "recency_status": status}


def rank_metric_year(observations: Iterable[dict], countries: Iterable[dict], metric_id: str, ranking_year: int) -> dict:
    cohort = list(countries)
    by_iso = {row["iso3"]: row for row in observations if row["metric_id"] == metric_id and row["year"] == ranking_year and row.get("value") is not None and _analytical_observation(row)}
    history: dict[str, list[dict]] = defaultdict(list)
    metric_rows = []
    for row in observations:
        if row["metric_id"] == metric_id and row.get("value") is not None and _analytical_observation(row):
            history[row["iso3"]].append(row)
            metric_rows.append(row)
    metric_max_year = max((row["year"] for row in metric_rows), default=None)
    for rows in history.values(): rows.sort(key=lambda row: row["year"])
    ranked_iso = sorted(by_iso, key=lambda iso: (-by_iso[iso]["value"], iso))
    ranks = {iso: index + 1 for index, iso in enumerate(ranked_iso)}
    ranked_count = len(ranked_iso); cohort_size = len(cohort)
    result = []
    for country in cohort:
        iso = country["iso3"]; observed = by_iso.get(iso); latest = history.get(iso, [])[-1] if history.get(iso) else None
        prior = next((row for row in reversed(history.get(iso, [])) if row["year"] == ranking_year - 1), None)
        result.append({
            "analytical_entity_id": country.get("analytical_entity_id", country.get("country_id")), "iso3": iso, "country": country["name"],
            "analytical_eligibility": country.get("analytical_eligibility", "included"), "metric_id": metric_id,
            "ranking_year": ranking_year, "rank": ranks.get(iso), "value": observed["value"] if observed else None,
            "observation_year": observed["year"] if observed else None, "prior_comparable_year": prior["year"] if prior else None,
            "prior_comparable_value": prior["value"] if prior else None, "latest_historical_year": latest["year"] if latest else None,
            "latest_historical_value": latest["value"] if latest else None, "metric_max_year": metric_max_year,
            "lag_years": recency(latest["year"] if latest else None, metric_max_year)["lag_years"],
            "recency_status": recency(latest["year"] if latest else None, metric_max_year)["recency_status"],
            "missing_reason": None if observed else "no_observation_in_ranking_year",
            "ranked_entity_count": ranked_count, "cohort_size": cohort_size,
            "coverage_ratio": ranked_count / cohort_size if cohort_size else 0,
        })
    return {"metric_id": metric_id, "ranking_year": ranking_year, "ranked_entity_count": ranked_count, "cohort_size": cohort_size, "coverage_ratio": ranked_count / cohort_size if cohort_size else 0, "rows": sorted(result, key=lambda row: (row["rank"] is None, row["rank"] or 10**9, row["iso3"]))}


def ranking_asset(observations: list[dict], countries: list[dict], metric: dict) -> dict:
    maximum_ranking_year = metric.get("ranking_year")
    years = sorted({row["year"] for row in observations if row["metric_id"] == metric["metric_id"] and row.get("value") is not None and _analytical_observation(row) and (maximum_ranking_year is None or row["year"] <= maximum_ranking_year)}, reverse=True)
    rankings = {str(year): rank_metric_year(observations, countries, metric["metric_id"], year) for year in years}
    lookup = {(row["iso3"], row["year"]): row["value"] for row in observations if row["metric_id"] == metric["metric_id"] and row.get("value") is not None}
    for year, ranking in ((int(key), value) for key, value in rankings.items()):
        for row in ranking["rows"]:
            row["changes"] = {str(window): change_value(row["value"], lookup.get((row["iso3"], year - window)), window, metric["change_transformation"]) for window in metric["change_windows"]}
            row["change_transformation"] = metric["change_transformation"]
    return {"schema_version": "1.0", "metric_id": metric["metric_id"], "default_ranking_year": years[0] if years else None, "available_ranking_years": years, "rankings": rankings}


def indexed_trajectory(rows: Iterable[dict], base_year: int) -> list[dict]:
    series = sorted((row for row in rows if row.get("value") is not None), key=lambda row: row["year"])
    base = next((row["value"] for row in series if row["year"] == base_year), None)
    return [{**row, "indexed_value": None if base in (None, 0) else row["value"] / base * 100} for row in series]


def change_value(current: Optional[float], previous: Optional[float], elapsed_years: int, transformation: str) -> Optional[float]:
    if current is None or previous is None or elapsed_years <= 0: return None
    if transformation == "percentage_point_change": return current - previous
    if transformation == "cagr":
        if current < 0 or previous <= 0: return None
        return ((current / previous) ** (1 / elapsed_years) - 1) * 100
    if transformation == "percent_change":
        if previous == 0: return None
        return (current / previous - 1) * 100
    raise ValueError(f"Unsupported change transformation: {transformation}")


def country_profile(observations: list[dict], countries: list[dict], metrics: list[dict], iso3: str) -> dict:
    country = next(row for row in countries if row["iso3"] == iso3)
    result = {"country": country, "metrics": {}}
    for metric in metrics:
        rows = sorted((row for row in observations if row["metric_id"] == metric["metric_id"] and row["iso3"] == iso3 and row.get("value") is not None and _analytical_observation(row)), key=lambda row: row["year"])
        max_year = metric.get("ranking_year") or max((row["year"] for row in observations if row["metric_id"] == metric["metric_id"] and row.get("value") is not None and _analytical_observation(row)), default=None)
        latest = rows[-1] if rows else None
        ranking = rank_metric_year(observations, countries, metric["metric_id"], max_year) if max_year else None
        rank_row = next((row for row in ranking["rows"] if row["iso3"] == iso3), None) if ranking else None
        values = [row["value"] for row in ranking["rows"] if row["value"] is not None] if ranking else []
        result["metrics"][metric["metric_id"]] = {"latest": latest, "recency": recency(latest["year"] if latest else None, max_year), "ranking": rank_row, "cohort_median": median(values) if values else None, "coverage": {"earliest_year": rows[0]["year"] if rows else None, "latest_year": rows[-1]["year"] if rows else None, "observation_count": len(rows)}}
    return result
