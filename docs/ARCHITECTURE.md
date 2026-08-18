# Architecture

## Layers

1. **Adapter** — a generic `SourceAdapter` contract owns transport, pagination, retries, caching, and source schema checks.
2. **Raw** — complete source responses plus checksums, preserved unchanged under `data/raw/YYYY-MM-DD/`.
3. **Normalized** — long-form observations keyed by `(iso3, reference_period, metric_id)` with durable lineage identifiers.
4. **Registry + validation** — declarative metric metadata joins to canonical observations before structural validation.
5. **Analytics** — the reproducible Top-50 universe, ranks, coverage, latest observations, and indexed comparisons.
6. **Application** — dependency-free HTML/CSS/JavaScript using precomputed in-memory indexes; per-metric shards are emitted for future lazy loading.

## Canonical logical schemas

### countries

`iso2`, `iso3`, `name`, `region`, `income_group`, `gdp_rank`, `reference_year`, `nominal_gdp`

### metrics

`metric_id`, `name`, `definition`, `unit`, `family`, `format`, `source_id`, `source_indicator`, `frequency`, `transformation`, `caveats`

### observations

`observation_id`, `country_id`, `iso3`, `reference_period`, `year`, `metric_id`, `raw_value`, `value`, `modeled_value`, `unit`, `frequency`, `source_id`, `source_dataset_id`, `source_indicator_id`, `retrieved_at`, `raw_snapshot_id`, `raw_record_index`, `transformation_id`, `pipeline_run_id`

### sources

`source_id`, `name`, `url`, `license`, `credibility`, `retrieved_at`

### dataset_updates

Every successful or failed run writes a JSON manifest keyed by `pipeline_run_id`, with timestamps, status, row counts, warnings/errors, snapshot checksums, and output paths.

## Adapter contract

Adapters return source-native records and preserve the full response before transformation. Downstream logic only consumes the canonical observation shape; adding an IMF adapter must not alter UI components or transformation function signatures.
