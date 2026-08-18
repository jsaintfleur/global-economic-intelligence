# Country-Year Freshness Matrix

Technical summary: the complete 350-row matrix reports each Top-50 country and Phase 1 metric without assigning a fresh/stale label. `years_behind_metric_max` is the metric-wide maximum observed year minus that country's latest observed year.

## Lag distribution

| Years behind metric maximum | Country-metric pairs |
| --- | --- |
| 0 | 313 |
| 1 | 3 |
| 10 | 1 |
| 15 | 1 |
| 17 | 1 |
| 2 | 1 |
| 21 | 1 |
| 24 | 2 |
| 25 | 1 |
| 3 | 1 |
| 30 | 7 |
| 32 | 1 |
| 34 | 1 |
| 6 | 1 |
| no observation | 15 |

Complete evidence: [`country_metric_freshness.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/country_metric_freshness.csv).
