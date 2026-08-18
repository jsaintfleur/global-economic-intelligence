# Current Ranking Implementation

Technical summary: universe rank is a common-2025 global-source-candidate GDP rank; metric tables are latest-available rankings within the fixed current Top-50. Historical rank is not implemented.

| Concern | Universe construction | Metric ranking tables |
| --- | --- | --- |
| Function | `gei.pipeline.build` + `rank_desc` | `buildIndex`, `latest`, `rankingTable` in `app/app.js` |
| Observation year | Common year 2025 | Each country latest non-null year |
| Missing values | Excluded from reference-year candidate values; no rank | Sorted after observed values; “Not available”; no displayed rank |
| Tie handling | Sequential rank, GDP descending then ISO3 ascending | No shared-rank policy and no explicit secondary tie key |
| Scope | All valid non-aggregate source candidates, then select 50 | Current Top-50 universe only |
| Historical rank | Not applicable | Not implemented; therefore neither global nor current-Top-50 historical rank |

Machine-readable evidence: [`ranking_implementation.json`](../../data/audit/release_e9182edbdb3e275e19ca/ranking_implementation.json).

## Audit note

The current production path is `gei.pipeline.build`. The similarly named universe tests in `tests/test_universe.py` import `pipelines.build`, so they do not directly execute this production selection path.
