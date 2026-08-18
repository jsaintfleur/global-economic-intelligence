# Scale test

Run on 2026-08-17 with `python3 scripts/scale_test.py`. Fixtures are explicitly synthetic and contain no economic claims.

| Shape | Observations | Compact JSON | Generate | Serialize | Peak Python memory |
|---|---:|---:|---:|---:|---:|
| 50 economies × 100 metrics × 30 years | 150,000 | 30.7 MB | 1.524 s | 1.879 s | 120.0 MB |
| 200 economies × 100 metrics × 30 years | 600,000 | 123.0 MB | 6.059 s | 7.719 s | 480.6 MB |

The dominant limit is browser transfer/parse cost, not transformation time. A monolithic payload is acceptable at the current 11,308 normalized observations but not at 100–200 metrics. The pipeline now emits a small catalog and one observation shard per metric. The current UI also builds metric/country/series/latest indexes once at startup, removing repeated full-panel scans. Switching runtime loading from the monolith to on-demand shards is the next scale step when metric count materially expands.

The 200-economy fixture's Python peak also justifies streaming writers for a future all-country analytical product. That optimization is unnecessary for the current Top-50 application snapshot.
