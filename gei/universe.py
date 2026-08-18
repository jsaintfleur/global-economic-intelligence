from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from .transformations import rank_desc


@dataclass(frozen=True)
class UniverseGDPObservation:
    analytical_entity_id: str
    iso3: str
    year: int
    value: float
    source_id: str
    source_indicator_id: str


class UniverseGDPProvider(Protocol):
    provider_id: str
    def observations(self) -> Iterable[UniverseGDPObservation]: ...


class NormalizedGDPProvider:
    def __init__(self, rows: Iterable[dict], provider_id: str = "world_bank_wdi"):
        self.provider_id = provider_id; self._rows = list(rows)
    def observations(self) -> Iterable[UniverseGDPObservation]:
        return [UniverseGDPObservation(row.get("analytical_entity_id", row["country_id"]), row["iso3"], row["year"], row["value"], row["source_id"], row["source_indicator_id"]) for row in self._rows if row.get("value") is not None]


def select_universe(provider: UniverseGDPProvider, entities: dict[str, dict], top_n: int = 50, minimum_observations: int = 50) -> tuple[int, list[dict], list[dict]]:
    eligible = {iso: row for iso, row in entities.items() if row.get("analytical_eligibility") == "included"}
    rows = [row for row in provider.observations() if row.iso3 in eligible]
    years = sorted({row.year for row in rows}, reverse=True)
    reference_year = next((year for year in years if sum(row.year == year for row in rows) >= minimum_observations), None)
    if reference_year is None: raise ValueError("No GDP year meets the approved analytical-cohort completeness threshold")
    values = {row.iso3: row.value for row in rows if row.year == reference_year}
    selected = sorted(values, key=lambda iso: (-values[iso], iso))[:top_n]
    ranks = rank_desc(values)
    universe = [{**eligible[iso], "iso3": iso, "gdp_rank": ranks[iso], "reference_year": reference_year, "nominal_gdp": values[iso]} for iso in selected]
    excluded = [{"iso3": iso, "analytical_entity_id": row["analytical_entity_id"], "analytical_eligibility": row["analytical_eligibility"], "reason": "not_included_by_eligibility_policy"} for iso, row in entities.items() if row.get("analytical_eligibility") != "included"]
    return reference_year, universe, excluded
