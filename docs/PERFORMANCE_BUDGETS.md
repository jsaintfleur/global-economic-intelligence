# Atlas performance budgets

Atlas remains a dependency-free static application. Performance budgets are checked against uncompressed source assets so regressions remain visible before CDN compression.

| Surface | Budget | Current measurement |
| --- | ---: | ---: |
| Application JavaScript | ≤ 75 KB | 63.5 KB |
| Design-system CSS | ≤ 30 KB | 22.1 KB |
| Initial catalog | ≤ 75 KB | 69.6 KB |
| Individual metric shard | ≤ 1.5 MB | 1.22 MB maximum |
| Initial analytical metric requests | ≤ 5 | 5 on Overview |
| First static render on local build | ≤ 1.5 s | under 1.0 s in browser QA |
| Selector/navigation response | ≤ 150 ms target | synchronous render after cached shard |

The complete `dist/` release is approximately 25 MB because it includes seven historical metric shards, exact-year ranking assets, 50 country profiles, coverage, and the compatibility payload. Only the catalog and Overview's declared assets load initially; other analytical data remains lazy-loaded.

Large future source additions should reduce precision, paginate, aggregate, or split assets before increasing these budgets. Cosmetic libraries are not sufficient justification for a budget increase.
