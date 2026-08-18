from __future__ import annotations

from collections import defaultdict

from .analytics import recency


def coverage_matrix(observations: list[dict], countries: list[dict], metrics: list[dict], start_year: int, end_year: int) -> dict:
    cm=defaultdict(list); my=defaultdict(set); cy=defaultdict(set)
    for row in observations:
        cm[(row["iso3"],row["metric_id"])].append(row["year"]);my[(row["metric_id"],row["year"])].add(row["iso3"]);cy[(row["iso3"],row["year"])].add(row["metric_id"])
    metric_max={metric:max(year for (candidate,year),values in my.items() if candidate==metric and values) for metric in {row["metric_id"] for row in observations}}
    country_metric=[]
    for country in countries:
        for metric in metrics:
            years=cm.get((country["iso3"],metric["metric_id"]),[]); latest=max(years) if years else None
            country_metric.append({"iso3":country["iso3"],"country":country.get("name",country["iso3"]),"metric_id":metric["metric_id"],"observation_count":len(years),"earliest_year":min(years) if years else None,"latest_year":latest,"expected_periods":end_year-start_year+1,**recency(latest,metric_max.get(metric["metric_id"]))})
    metric_year=[{"metric_id":metric,"year":year,"country_count":len(values)} for (metric,year),values in sorted(my.items())]
    country_year=[{"iso3":iso,"year":year,"metric_count":len(values)} for (iso,year),values in sorted(cy.items())]
    inventory=[]
    for metric in metrics:
        rows=[row for row in observations if row["metric_id"]==metric["metric_id"]];covered={row["iso3"] for row in rows}
        latest_year=max((row["year"] for row in rows),default=None); ranking_year_count=len({row["iso3"] for row in rows if row["year"]==latest_year}) if latest_year else 0
        inventory.append({"metric_id":metric["metric_id"],"display_name":metric["display_name"],"source_id":metric["source_id"],"ever_observed_country_count":len(covered),"ranking_year_observed_country_count":ranking_year_count,"missing_all_years_country_count":len(countries)-len(covered),"ranking_year_missing_country_count":len(countries)-ranking_year_count,"country_count":len(covered),"earliest_year":min((row["year"] for row in rows),default=None),"latest_year":latest_year,"ranking_year":latest_year,"observation_count":len(rows),"missing_country_count":len(countries)-len(covered)})
    return {"schema_version":"1.1","country_metric":country_metric,"metric_year":metric_year,"country_year":country_year,"inventory":inventory}
