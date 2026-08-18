# Phase 2 engineering readiness

## Ready

- Metric, source, transformation, and country metadata are versioned registries.
- Adapter contracts, lineage, release manifests, diffs, regression gates, coverage matrices, and offline compliance fixtures are source-agnostic.
- Reference periods have a formatting abstraction for annual, quarterly, and monthly data.
- Metric shards, URL-addressable state, in-memory request deduplication, and standardized chart inputs support substantially broader catalogs.
- Static packaging, asset checksums, cache guidance, and failure states support deployment.

## Technical blockers before materially larger scale

- The pipeline still constructs the full normalized all-country list in memory; a 200-country/100-metric build should use streaming or a columnar intermediate store.
- Overview currently downloads three full metric shards. A purpose-built overview aggregate would reduce initial transfer further.
- The application retains loaded shards for the session. Very broad interactive exploration needs an eviction policy or worker-backed columnar store.
- Data Explorer caps DOM rendering but does not yet implement full virtualization.
- Monthly/quarterly identity and uniqueness validation requires a period-aware canonical key rather than the annual `year` compatibility field.
- Release snapshots need external object storage and retention automation before continuous production refreshes.
- Multi-adapter orchestration needs a source router; the current build accepts one adapter instance per run.

These are engineering constraints only and do not recommend or define future economic features.
