# Missing-Data Summary

Technical summary: Phase 1 preserves missing values and uses identity transformations. No transformation removes a normalized observation. Structural rejections occur before the Top-50 panel is selected.

| Metric | No observations | Latest behind metric max | Rejected raw rows | Structural rejection reasons |
| --- | --- | --- | --- | --- |
| gdp_current_usd | None | None | 2139 | missing_value: 411; unknown_or_aggregate_country: 1728 |
| gdp_per_capita_current_usd | None | None | 2139 | missing_value: 411; unknown_or_aggregate_country: 1728 |
| gdp_growth_pct | None | None | 2244 | missing_value: 516; unknown_or_aggregate_country: 1728 |
| population | None | None | 1728 | unknown_or_aggregate_country: 1728 |
| inflation_cpi_pct | None | USA (2024), ARG (2024) | 3360 | missing_value: 1632; unknown_or_aggregate_country: 1728 |
| unemployment_pct | None | None | 3009 | missing_value: 1281; unknown_or_aggregate_country: 1728 |
| central_government_debt_pct_gdp | CHN, JPN, FRA, SAU, BEL, IRL, ARG, SWE, AUT, VNM, ROU, HKG, IRN, NGA, DZA | DEU (1990), IND (2018), ITA (1992), AUS (2022), IDN (2009), NLD (1994), POL (1994), ISR (1999), NOR (1994), PHL (2014), DNK (1994), BGD (2003), PAK (2000), CZE (1994), EGY (2007), CHL (2000), PRT (1994), PER (2021), FIN (1994), KAZ (2023) | 7895 | missing_value: 6167; unknown_or_aggregate_country: 1728 |

Exact country-year gaps: [`missing_country_year_ranges.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/missing_country_year_ranges.csv). Structured summary: [`missing_data_summary.json`](../../data/audit/release_c95979a1f2a0d628fbf3/missing_data_summary.json).
