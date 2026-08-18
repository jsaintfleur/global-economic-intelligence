# Data contracts and lineage

```text
Source Adapter
  → immutable RawSnapshot
  → CanonicalObservation
  → metric registry join
  → structural validation
  → declared transformation
  → analytics universe
  → application payload / export
```

## Observation identity

`observation_id` is a stable hash of source, source indicator, ISO3, and reference period. It is stable across identical refreshes. `pipeline_run_id` identifies a particular execution; `raw_snapshot_id` identifies exact source bytes; `raw_record_index` locates the upstream record within that snapshot.

The canonical uniqueness key for annual Phase 1 data is `(iso3, year, metric_id)`. Frequency-specific period keys can extend this without changing lineage fields.

## Run manifest

Every attempt writes `data/manifests/<pipeline_run_id>.json`, including failures. Manifests record requested indicators, raw/accepted/rejected/missing counts, warnings, errors, snapshots, outputs, timestamps, and code contract version.

## Rejections

Rejected rows are written separately with source indicator, raw index, source country code, source period, and structural reason. Missing values remain absent from normalized observations and are never imputed by the adapter.
