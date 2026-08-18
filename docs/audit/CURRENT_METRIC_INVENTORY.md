# Current Metric Inventory

Technical summary: this is a direct inventory of the current application payload. Counts refer only to the fixed Top-50 universe; no freshness judgment is applied.

| Metric | Display | Source / indicator | Unit | Transform | Obs. | Countries | Years | Latest-year median / min / max | Missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gdp_current_usd | Nominal GDP | world_bank_wdi / NY.GDP.MKTP.CD | current US$ | identity | 1800 | 50 | 1990-2025 | 2025.0 / 2025 / 2025 | 0 |
| gdp_per_capita_current_usd | GDP per capita | world_bank_wdi / NY.GDP.PCAP.CD | current US$ per person | identity | 1800 | 50 | 1990-2025 | 2025.0 / 2025 / 2025 | 0 |
| gdp_growth_pct | Real GDP growth | world_bank_wdi / NY.GDP.MKTP.KD.ZG | % annual change | identity | 1796 | 50 | 1990-2025 | 2025.0 / 2025 / 2025 | 0 |
| population | Population | world_bank_wdi / SP.POP.TOTL | people | identity | 1800 | 50 | 1990-2025 | 2025.0 / 2025 / 2025 | 0 |
| inflation_cpi_pct | CPI inflation | world_bank_wdi / FP.CPI.TOTL.ZG | % annual change | identity | 1754 | 50 | 1990-2025 | 2025.0 / 2024 / 2025 | 0 |
| unemployment_pct | Unemployment | world_bank_wdi / SL.UEM.TOTL.ZS | % of total labor force (modeled ILO estimate) | identity | 1750 | 50 | 1991-2025 | 2025.0 / 2025 / 2025 | 0 |
| central_government_debt_pct_gdp | Central government debt | world_bank_wdi / GC.DOD.TOTL.GD.ZS | % of GDP | identity | 608 | 35 | 1990-2024 | 2021 / 1990 / 2024 | 15 |

Metric registry fingerprint: `7de47f69e8f16b66`. Source dataset for every row: `world_development_indicators`. Exact fields are in [`current_metric_inventory.csv`](../../data/audit/release_e9182edbdb3e275e19ca/current_metric_inventory.csv) and the adjacent JSON.
