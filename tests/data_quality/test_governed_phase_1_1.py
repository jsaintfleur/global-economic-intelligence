import json
from pathlib import Path

import pytest
import yaml

from gei.capabilities import metric_capabilities
from gei.config import load_metric_registry


ROOT = Path(__file__).resolve().parents[2]


def payload():
    return json.loads((ROOT / "app" / "data" / "dashboard.json").read_text())


@pytest.mark.decision("D-001")
@pytest.mark.test_id("TEST-U-002")
def test_production_universe_contains_pinned_taiwan():
    data = payload()
    taiwan = next(country for country in data["countries"] if country["iso3"] == "TWN")
    assert data["meta"]["universe_provider_id"] == "imf_weo"
    assert data["meta"]["candidate_universe_complete"] is True
    assert (taiwan["gdp_rank"], taiwan["nominal_gdp"]) == (22, 801_495_464_000)


@pytest.mark.decision("D-001")
@pytest.mark.test_id("TEST-U-002b")
def test_production_universe_has_pinned_boundary_and_cardinality():
    data = payload()
    assert len(data["countries"]) == 50
    assert [(row["gdp_rank"], row["iso3"]) for row in data["countries"][-3:]] == [
        (48, "FIN"),
        (49, "PER"),
        (50, "KAZ"),
    ]
    assert [(row["rank"], row["iso3"]) for row in data["meta"]["universe_exclusions"][:2]] == [
        (51, "IRQ"),
        (52, "DZA"),
    ]


@pytest.mark.decision("D-001")
@pytest.mark.test_id("TEST-U-002c")
def test_fiscal_year_boundaries_are_actual_at_reference_year():
    data = payload()
    rows = {
        row["iso3"]: row
        for row in data["observations"]
        if row["metric_id"] == "gdp_current_usd"
        and row["year"] == data["meta"]["reference_year"]
    }
    for iso3 in ("IND", "BGD", "IRN", "EGY", "PAK"):
        assert rows[iso3]["latest_actual_raw"] == "FY2024/25"
        assert rows[iso3]["latest_actual_year"] == 2024
        assert rows[iso3]["observation_class"] == "actual"


@pytest.mark.decision("D-001")
@pytest.mark.test_id("TEST-U-003")
def test_world_bank_cross_check_difference_has_structural_composition():
    data = payload()
    weo = {country["iso3"] for country in data["countries"]}
    cross_check = json.loads(
        (ROOT / "governance" / "fixtures" / "world_bank_top50_2024.json").read_text()
    )
    assert cross_check["source_id"] == "world_bank_wdi"
    assert cross_check["indicator"] == "NY.GDP.MKTP.CD"
    assert cross_check["year"] == data["meta"]["reference_year"]
    wb = set(cross_check["iso3"])
    assert weo - wb == {"TWN"}, f"WEO-only={sorted(weo-wb)}, WB-only={sorted(wb-weo)}"
    assert len(wb - weo) == 1, f"WEO-only={sorted(weo-wb)}, WB-only={sorted(wb-weo)}"


@pytest.mark.decision("D-003")
@pytest.mark.test_id("TEST-E-001")
def test_selected_entities_are_explicitly_eligible_and_not_consolidated():
    adjudication = yaml.safe_load(
        (ROOT / "governance" / "entities" / "eligibility_adjudication.yaml").read_text()
    )["entities"]
    for country in payload()["countries"]:
        decision = adjudication[country["iso3"]]
        assert decision["eligibility"] == "eligible"
        assert decision["consolidated_into"] is None


@pytest.mark.decision("D-004")
@pytest.mark.test_id("TEST-C-001")
def test_each_metric_has_one_primary_source_and_no_spliced_history():
    data = payload()
    for metric in data["metrics"]:
        sources = {
            (row["source_id"], row["source_indicator_id"])
            for row in data["observations"]
            if row["metric_id"] == metric["metric_id"]
        }
        assert sources <= {(metric["source_id"], metric["source_indicator_id"])}


@pytest.mark.decision("D-007")
@pytest.mark.test_id("TEST-C-002")
def test_comparability_and_scope_govern_capabilities():
    assert metric_capabilities(
        {"comparability_class": "C", "population_scope": "universal"}
    )["cross_country_ranking"] is False
    assert metric_capabilities(
        {"comparability_class": "A", "population_scope": "subset:borrowers"}
    )["comparison_axis"] is False
    assert metric_capabilities(
        {"comparability_class": "B", "population_scope": "universal"}
    )["cross_country_ranking"] is True


@pytest.mark.decision("D-008")
@pytest.mark.test_id("TEST-F-002")
def test_approved_source_substitutions_are_exact():
    mappings = {
        metric["metric_id"]: (metric["source_id"], metric["source_indicator_id"])
        for metric in load_metric_registry()
    }
    assert mappings["general_government_gross_debt_pct_gdp"] == (
        "imf_weo",
        "GGXWDG_NGDP",
    )
    assert mappings["general_government_net_lending_pct_gdp"] == (
        "imf_weo",
        "GGXCNL_NGDP",
    )
    assert mappings["inflation_cpi_pct"] == ("imf_weo", "PCPIPCH")
    assert mappings["unemployment_pct"] == ("world_bank_wdi", "SL.UEM.TOTL.ZS")


@pytest.mark.decision("D-009")
@pytest.mark.test_id("TEST-F-003")
def test_excluded_indicators_are_absent_from_registry():
    indicators = {metric["source_indicator_id"] for metric in load_metric_registry()}
    assert indicators.isdisjoint(
        {
            "DT.DOD.DECT.CD",
            "FR.INR.RINR",
            "FR.INR.LEND",
            "GC.DOD.TOTL.GD.ZS",
            "SL.UEM.TOTL.NE.ZS",
        }
    )
