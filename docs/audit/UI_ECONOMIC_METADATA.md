# UI Economic Metadata

Technical summary: the app exposes observation years and missing-value states prominently in analytical views, while full metric definitions are concentrated on Methodology. This is a visibility inventory, not a redesign proposal.

| Page | Units | Source | Observation year | Missing-value state | Rank | Definition | Retrieval date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Overview | Yes | Yes | Yes | Limited | Yes | No | Sidebar retrieval snapshot |
| Rankings | Via metric/value formatting | Yes | Yes | Yes | Yes | No | Sidebar retrieval snapshot |
| Compare | Yes | Sidebar only | Yes | Chart gaps / absent latest cards | Universe rank in cards | No | Sidebar retrieval snapshot |
| Country Explorer | Yes | Sidebar only | Yes | Yes | GDP universe rank | No | Sidebar retrieval snapshot |
| Data Explorer | Yes | Indicator/source columns | Yes | Only observed normalized rows are exported | No | No | Per-row retrieval timestamp |
| Methodology | Yes | Yes | Retrieval date | Policy described | Formula described | Yes | Yes |
| Diagnostics (URL-only) | No | Source IDs | No | No | No | No | Build generated timestamp |

Evidence basis: current `app/app.js` rendering functions plus the existing automated browser QA performed for this release. Machine matrix: [`ui_economic_metadata.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/ui_economic_metadata.csv).
