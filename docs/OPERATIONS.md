# Data operations

## Refresh lifecycle

1. `make validate-config`
2. `make data`
3. inspect `data/releases/latest.json`
4. inspect the release regression report and any `data/diffs/*.md`
5. `make inventory`
6. `make test`
7. `make build`

Each run writes a pipeline manifest even on failure. A successful content change creates a new release ID and old→new diff. An identical rerun retains the same release ID while recording a new pipeline-run manifest.

Regression policy lives in `config/regression_rules.json`. Blocking rules protect structural integrity: missing provenance, duplicate canonical keys, missing metric shards, and removed metrics. Data revisions, source mapping changes, latest-year regressions, coverage loss, and row-count changes remain visible findings whose severities and thresholds can be changed declaratively.

Use `python3 -m scripts.diff_snapshots OLD NEW` for an explicit comparison. Absolute and percentage changes are emitted where the old value is nonzero. No economic materiality threshold is embedded in code.
