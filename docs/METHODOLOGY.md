# Phase 1 methodology

## Top-50 selection

The universe is ranked using nominal GDP in current US dollars (`NY.GDP.MKTP.CD`). The reference year is the most recent year with at least 150 non-aggregate economy observations. The 50 highest observations define the universe for the entire snapshot. Other metrics do not trigger substitutions.

This is a pragmatic completeness rule, not an economic claim. The threshold and treatment of territories require economist review before production publication.

## Observation-year policy

Rankings outside the GDP universe show each country's latest available value and display that value's year. Atlas does not imply that these latest values are synchronous. Common-year comparison should be added as an explicit alternate mode, not silently substituted.

## Missing data

No interpolation occurs in Phase 1. `raw_value` is preserved, `modeled_value` remains null, and unavailable cells display “Not available.” Coverage counts observed years within the configured window.

## Formulas

- Percentage change: `(current / previous − 1) × 100`
- CAGR: `((end / start)^(1 / elapsed years) − 1) × 100`
- Indexed comparison: `(value_t / value_base_year) × 100`
- Descending rank: order non-null values from greatest to least; missing values receive no rank

## Indicator scope

Nominal GDP and GDP per capita use current US dollars. GDP growth is the World Bank constant-local-currency annual growth series. CPI inflation is annual percent change. Unemployment is the modeled ILO estimate. Debt is central-government debt, not general-government debt.

