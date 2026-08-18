# Current Ranking Implementation

Technical summary: universe selection uses explicit eligibility and common-2025 provider GDP. Every metric ranking uses one exact year; historical ranks are recomputed within their own year.

| Concern | Universe construction | Metric ranking tables |
| --- | --- | --- |
| Function | `gei.universe.select_universe` via `gei.pipeline.build` | `gei.analytics.ranking_asset` |
| Observation year | Common year 2025 | One exact declared year |
| Missing values | Provider/eligibility limitations disclosed | Visible with null rank/value; historical context separate |
| Tie handling | GDP descending then ISO3 ascending | Value descending then ISO3 ascending |
| Scope | Explicitly included analytical entities | Current analytical cohort |
| Historical rank | Not applicable | Recomputed within each historical year |

Machine-readable evidence: [`ranking_implementation.json`](../../data/audit/release_c95979a1f2a0d628fbf3/ranking_implementation.json).

## Audit note

`tests/test_universe.py` now exercises `gei.universe.select_universe`, the function called by the production pipeline. Legacy compatibility coverage is isolated under `tests/legacy/`.
