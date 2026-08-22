from __future__ import annotations


def metric_capabilities(metric: dict) -> dict:
    comparability = metric["comparability_class"]
    scope = metric["population_scope"]
    cross_country = comparability in {"A", "B"} and scope == "universal"
    return {
        "cross_country_ranking": cross_country,
        "comparison_axis": cross_country,
        "country_profile": True,
        "requires_comparability_warning": comparability == "C",
    }
