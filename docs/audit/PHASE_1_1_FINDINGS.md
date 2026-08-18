# Phase 1.1 Audit Findings

This addendum classifies the release evidence that must shape Phase 1.1. It does not alter release `release_e9182edbdb3e275e19ca`.

## SOURCE PROBLEMS

- World Bank WDI `GC.DOD.TOTL.GD.ZS` is a central-government debt series sourced by WDI from IMF Government Finance Statistics. It is not a general-government gross-debt series. Its Top-50 coverage is sparse and temporally uneven.
- The World Bank country dimension used by the production pipeline contains no Taiwan record or World Bank country code. Same-year GDP consistency therefore applies only to entities present in that source; it does not establish candidate-universe completeness.
- Current country metadata supplies no reviewed sovereignty or analytical-eligibility classification. `territory_classification` is null for all 50 selected entities.

## METHODOLOGY PROBLEMS

- Current non-universe metric rankings use each economy's latest available value, allowing different observation years in one ranking.
- “Debt coverage” previously referred to two different measures. In release evidence, 35 of 50 economies have at least one debt observation anywhere in 1990–2025. Exactly 15 of 50 have a debt observation in 2024, the metric-wide latest populated year. The figures are consistent once the time criterion is stated.
- A common GDP reference year solves temporal comparability among observed candidates but does not solve source-universe omissions such as Taiwan.

## IMPLEMENTATION PROBLEMS

- Production universe construction is implemented in `gei.pipeline.build`; a separate legacy implementation remains in `pipelines.build`.
- There is no explicit reviewed analytical-entity eligibility field. The pipeline currently treats every non-aggregate World Bank country-dimension entry as a candidate.
- Historical rank is not implemented, and latest-observation ranking is performed in frontend code.

## TESTING PROBLEMS

- `tests/test_universe.py` imports `pipelines.build`, so its three universe tests do not execute the production `gei.pipeline.build` selection path.
- There are no production-path assertions for candidate eligibility, Taiwan/source-universe handling, same-year metric ranks, or missing rank when a country has no value in the ranking year.
- UI tests do not currently enforce observation-year and freshness metadata across ranking states.

## PRODUCT/UX PROBLEMS

- A ranking can look synchronous while mixing years; displaying the year reduces but does not remove the methodological ambiguity.
- The UI does not distinguish “has any historical observation” from “has an observation in the ranking year.”
- Candidate-universe limitations, including entities absent from the World Bank dimension, are not exposed near the Top-50 methodology.

## Debt reconciliation

| Coverage definition | Result | Evidence |
| --- | --- | --- |
| Any accepted observation during 1990–2025 | 35/50 | 608 release observations; 15 economies have no observations |
| Observation in metric-wide latest year (2024) | 15/50 | USA, GBR, RUS, CAN, BRA, ESP, KOR, MEX, TUR, CHE, SGP, THA, MYS, COL, ZAF |
| Observation in 2025 | 0/50 | The series' release maximum is 2024 |

The discrepancy is not caused by a different metric, country universe, or transformation. It is caused by **historical-ever coverage versus latest-common-year coverage**.

Authoritative source metadata: [World Bank indicator `GC.DOD.TOTL.GD.ZS`](https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS). Release evidence: [`CURRENT_DEBT_IMPLEMENTATION.md`](CURRENT_DEBT_IMPLEMENTATION.md) and [`country_metric_freshness.csv`](../../data/audit/release_e9182edbdb3e275e19ca/country_metric_freshness.csv).
