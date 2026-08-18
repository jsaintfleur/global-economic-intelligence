# Changelog

## 0.1.0

- Established raw, normalized, analytics, and application layers.
- Added World Bank WDI adapter and seven-indicator Phase 1 pipeline.
- Added reproducible Top-50 construction and provenance-preserving payload.
- Added Overview, Rankings, Compare, Country Explorer, Data Explorer, Methodology, and CSV export.
- Added transformation and payload-contract tests.

## 0.2.0 — Engineering hardening

- Replaced duplicated metric declarations with a validated versioned canonical registry.
- Introduced a generic source-adapter interface; World Bank is now one implementation.
- Added stable observation, raw snapshot, and pipeline-run identifiers with full lineage fields.
- Added raw SHA-256 checksums, raw record indexes, explicit rejection output, and historical success/failure manifests.
- Added structural validation for metric mappings, observation schemas, ISO3s, orphan records, duplicate keys/IDs, invalid years/values, and missing provenance.
- Expanded the deterministic suite from 11 to 24 tests across unit, integration, and data-quality groups.
- Added CI, Make targets, adapter/metric/data-contract documentation, and scale-test tooling.
- Added one-time frontend indexing, enriched exports, and per-metric data shards for future lazy loading.
- Preserved unresolved economic questions and did not modify `CLAUDE_TO_CODEX.md`.

## 0.3.0 — Operational maturity

### Application changes

- Switched the frontend to catalog-first, on-demand metric shard loading with request deduplication, retry states, URL-addressable view/filter state, centralized formatters, and developer timing instrumentation.
- Added accessible focus treatment, skip navigation, labeled controls, table semantics, chart fallbacks, responsive mobile navigation, and safer rendering of source strings.
- Added static deployment packaging, asset checksums, cache-header guidance, and a development diagnostics view at `?view=diagnostics`.

### Data changes

- Added country×metric, metric×year, and country×year coverage matrices plus a command-line inventory.
- No economic observations, definitions, or source mappings were intentionally changed in this sprint.

### Metric definition changes

- None.

### Source changes

- Moved World Bank dataset attribution, license, endpoint, and adapter metadata into a versioned source registry; the active mapping is unchanged.

### Methodology changes

- None. Claude-owned questions remain deferred.

### Operational changes

- Added content-derived release IDs, formal release manifests, snapshot archives, configurable regression gates, machine/Markdown snapshot diffs, structured logs, schema-version documentation, offline fixture builds, adapter compliance tests, and expanded API-failure simulation.
