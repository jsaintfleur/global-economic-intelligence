# Adding a source adapter

Implement `gei.adapters.SourceAdapter`:

- `fetch_countries(retrieved_at) -> AdapterResult`
- `fetch_indicator(indicator_id, start, end, retrieved_at) -> AdapterResult`

An adapter owns pagination, retries/backoff, source schema checks, cache behavior, and immutable raw preservation. It returns source-native records plus a `RawSnapshot`; it does not make economic transformations.

`RawSnapshot` requires a durable ID, source and dataset identifiers, retrieval timestamp, relative path, record count, and SHA-256 checksum. Populate dataset version metadata when the upstream source exposes it.

Source-specific normalization should be implemented as an explicit mapping into `CanonicalObservation`. It must preserve a raw snapshot ID and raw record index. Malformed, missing, duplicate, and unmappable records belong in the rejection stream rather than being silently discarded.

Adapter tests must use deterministic fixture responses. Network-dependent smoke tests should be separate and excluded from default CI.

