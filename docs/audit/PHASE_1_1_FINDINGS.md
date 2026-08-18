# Phase 1.1 Audit Findings

This addendum classifies the evidence addressed by Phase 1.1 and is bound to release `release_c95979a1f2a0d628fbf3`.

## SOURCE PROBLEMS

- World Bank WDI `GC.DOD.TOTL.GD.ZS` is a central-government debt series sourced by WDI from IMF Government Finance Statistics. It is not a general-government gross-debt series. Its Top-50 coverage is sparse and temporally uneven.
- The World Bank country dimension used by the production pipeline contains no Taiwan record or World Bank country code. Same-year GDP consistency therefore applies only to entities present in that source; it does not establish candidate-universe completeness.
- World Bank source availability cannot supply a geopolitical classification. Phase 1.1 therefore uses an explicit analytical-eligibility registry with authoritative IDs and review metadata; it does not infer sovereignty.

## METHODOLOGY PROBLEMS

- The prior latest-available ranking method allowed mixed observation years. Phase 1.1 replaces it with exact-year ranking: only observations in the declared ranking year receive rank, and historical context never enters rank.
- “Debt coverage” previously referred to two different measures. In release evidence, 35 of 50 economies have at least one debt observation anywhere in 1990–2025. Exactly 15 of 50 have a debt observation in 2024, the metric-wide latest populated year. The figures are consistent once the time criterion is stated.
- A common GDP reference year solves temporal comparability among observed candidates but does not solve source-universe omissions such as Taiwan.

## IMPLEMENTATION PROBLEMS

- Production universe construction is implemented in `gei.pipeline.build`; a separate legacy implementation remains in `pipelines.build`.
- `config/analytical_entities.json` now supplies explicit eligibility and identifiers; `gei.universe.select_universe` is provider-neutral.
- `gei.analytics.ranking_asset` now computes exact-year and historical same-year ranks, recency, missing states, and metric-specific changes before frontend rendering.

## TESTING PROBLEMS

- `tests/test_universe.py` now imports the same `gei.universe.select_universe` function used by production; legacy coverage is isolated under `tests/legacy/`.
- Release fixtures assert Taiwan/source-universe disclosure, exact-year GDP, the 35/15 debt definitions, and USA/Argentina inflation missing ranks in 2025.
- Frontend contract tests enforce exact-year wording, missing states, provenance/export lineage, URL state, and Coverage navigation; rendered browser QA remains a release step.

## PRODUCT/UX PROBLEMS

- Rankings now state their exact year and coverage, keep missing entities visible below ranked observations, and label historical context separately.
- Coverage and overview views distinguish “ever observed” from “observed in ranking year.”
- Methodology and diagnostics disclose candidate-universe incompleteness and the Taiwan/provider limitation.

## Debt reconciliation

| Coverage definition | Result | Evidence |
| --- | --- | --- |
| Any accepted observation during 1990–2024 | 35/50 | 608 release observations; 15 economies have no observations |
| Observation in metric-wide latest year (2024) | 15/50 | USA, GBR, RUS, CAN, BRA, ESP, KOR, MEX, TUR, CHE, SGP, THA, MYS, COL, ZAF |
| Observation in 2025 | 0/50 | The series' release maximum is 2024 |

The discrepancy is not caused by a different metric, country universe, or transformation. It is caused by **historical-ever coverage versus latest-common-year coverage**.

Authoritative source metadata: [World Bank indicator `GC.DOD.TOTL.GD.ZS`](https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS). Release evidence: [`CURRENT_DEBT_IMPLEMENTATION.md`](CURRENT_DEBT_IMPLEMENTATION.md) and [`country_metric_freshness.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/country_metric_freshness.csv).
