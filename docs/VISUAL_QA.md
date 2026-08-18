# Visual QA fixtures

The checked-in screenshots are deterministic review fixtures captured from the static production build and real release `release_c95979a1f2a0d628fbf3`.

| Fixture | Viewport | State |
| --- | --- | --- |
| `visual-qa/overview-1440.png` | 1440 × 1000 | Overview, light |
| `visual-qa/economy-1280.png` | 1280 × 900 | China profile, light |
| `visual-qa/compare-1024.png` | 1024 × 900 | GDP comparison, indexed |
| `visual-qa/rankings-768.png` | 768 × 900 | Inflation 2025 ranking |
| `visual-qa/explore-390.png` | 390 × 844 | Scatter explorer, mobile |
| `visual-qa/overview-mobile-390.png` | 390 × 844 | Overview, mobile |
| `visual-qa/overview-dark-1280.png` | 1280 × 900 | Overview, dark |

Review criteria: no document-level horizontal overflow, clipped controls, overlapping labels, misleading zero states, inaccessible contrast, or hidden observation-year context. Tables may scroll within their bounded container on narrow screens. Mobile navigation is intentionally horizontally scrollable rather than compressing labels into ambiguous icons.

These fixtures are review evidence, not pixel-diff baselines. Font rendering can vary by operating system; semantic browser checks remain authoritative for content and state.
