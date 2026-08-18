# Adding a metric

Add one object to `config/metrics.json`. The registry is validated before any source request. A normal identity-transformed metric requires no Python or JavaScript edits when its source adapter already exists.

Required structural fields are enforced by `gei.validation.REQUIRED_METRIC_FIELDS`. Economic content—including description, unit, directionality, transformation, and missing-data policy—must come from the methodological owner. `directionality: not_assessed` is valid when no reviewed interpretation exists.

The source adapter is selected by `source_id`; it retrieves `source_indicator_id`. Normalization emits the registry's unit, frequency, transformation ID, and source mapping into every observation. The application builds selectors, labels, formatting, charts, and enriched exports from the registry payload.

Before merging:

1. Run `make check` and `make test`.
2. Run `make data` to produce a dated raw snapshot and manifest.
3. Inspect rejected observations and manifest warnings.
4. Verify the metric's missingness and observation years in Data Explorer.

