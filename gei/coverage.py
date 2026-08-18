from __future__ import annotations

from collections import defaultdict


def coverage_matrix(observations: list[dict], countries: list[dict], metrics: list[dict], start_year: int, end_year: int) -> dict:
    cm=defaultdict(list); my=defaultdict(set); cy=defaultdict(set)
    for row in observations:
        cm[(row["iso3"],row["metric_id"])].append(row["year"]);my[(row["metric_id"],row["year"])].add(row["iso3"]);cy[(row["iso3"],row["year"])].add(row["metric_id"])
    country_metric=[{"iso3":iso,"metric_id":metric,"observation_count":len(years),"earliest_year":min(years),"latest_year":max(years),"expected_periods":end_year-start_year+1} for (iso,metric),years in sorted(cm.items())]
    metric_year=[{"metric_id":metric,"year":year,"country_count":len(values)} for (metric,year),values in sorted(my.items())]
    country_year=[{"iso3":iso,"year":year,"metric_count":len(values)} for (iso,year),values in sorted(cy.items())]
    inventory=[]
    for metric in metrics:
        rows=[row for row in observations if row["metric_id"]==metric["metric_id"]];covered={row["iso3"] for row in rows}
        inventory.append({"metric_id":metric["metric_id"],"display_name":metric["display_name"],"source_id":metric["source_id"],"country_count":len(covered),"earliest_year":min((row["year"] for row in rows),default=None),"latest_year":max((row["year"] for row in rows),default=None),"observation_count":len(rows),"missing_country_count":len(countries)-len(covered)})
    return {"schema_version":"1.0","country_metric":country_metric,"metric_year":metric_year,"country_year":country_year,"inventory":inventory}
