# Phase 1.1 methodology

## Analytical entity universe

Atlas selects the production cohort through the explicit, versioned registry in `config/analytical_entities.json`. Only entities marked `included` are eligible. The pipeline does not infer sovereignty or territory status; eligibility changes require authoritative identifiers, a documented basis, and economic review.

The universe-selection function is source-neutral and currently receives normalized World Bank WDI nominal-GDP observations (`NY.GDP.MKTP.CD`). It chooses the latest year containing the required 50 eligible observations, ranks descending, resolves ties by ISO3, and returns exactly 50. All selected entities have 2025 GDP observations in the current release.

This same-year result does not prove candidate-universe completeness. World Bank WDI does not contain Taiwan as a GDP economy. Taiwan is therefore explicitly recorded as `pending_review`, with IMF WEO identifier `TWN` and no fabricated World Bank mapping. Adding an approved normalized provider is a separate reviewed source decision.

## Exact-year ranking policy

Every ranking declares one `ranking_year`. An entity receives a rank only when it has a non-null observation for that exact metric and year. Values sort descending, ties resolve by ISO3, and ranks are sequential among the observed subset. Missing entities remain visible below ranked entities with null rank and value. Their latest historical observation may be displayed only in a separately labelled context field; it never enters the ranking.

The default ranking year is the metric-wide maximum observed year. Historical ranking views recompute all ranks within the selected historical year and never reuse current ranks.

## Recency policy

Recency is structural metadata measured against each metric's maximum observation year:

- `current_year`: lag 0
- `prior_year`: lag 1
- `historical`: lag 2 or greater
- `unavailable`: no observation

Retrieval date never substitutes for observation year. In the current inflation ranking year, 2025, the USA and Argentina have latest observations in 2024; they are `prior_year`, remain unranked for 2025, and show 2024 only as historical context.

## Coverage definitions

“Ever observed” and “observed in the ranking year” answer different questions. For central-government debt, 35 of the current 50 have at least one observation anywhere in the history, while only 15 have an observation in the metric maximum year, 2024. Historical years span 1990–2024. The ranking coverage is therefore 15/50; it is not 35/50.

## Missing data and transformations

No interpolation, carry-forward, or modeled fallback occurs. `raw_value` is preserved and `modeled_value` remains null.

- GDP, GDP per capita, and population may be indexed to a user-selected base year and use CAGR for 1/5/10-year changes.
- Growth, inflation, unemployment, and debt remain in percentage-rate levels and use percentage-point changes.
- Indexed comparison: `(value_t / value_base_year) × 100`.
- CAGR: `((end / start)^(1 / elapsed years) − 1) × 100`.
- Percentage-point change: `current − previous`.

## Indicator scope

Nominal GDP and GDP per capita use current US dollars. GDP growth is the World Bank constant-local-currency annual growth series. CPI inflation is annual percent change. Unemployment is the modeled ILO estimate. Debt is central-government debt, not general-government debt.
