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

## Analytical entity registry

`config/analytical_entities.json` is the authoritative application eligibility layer. Each record contains a stable analytical entity ID, explicit eligibility state, effective dates, authoritative source identifiers, review basis, and policy version. Source availability is not treated as geopolitical classification.

## Phase 1.1 analytical assets

The catalog schema is `2.1`. In addition to canonical metric shards, it maps metric IDs to ranking shards and ISO3 codes to country-profile shards.

A ranking asset contains a default ranking year, available historical years, and one exact-year result per year. Every row exposes `ranking_year`, nullable `rank` and `value`, observation year, separately labelled latest historical context, metric maximum year, lag, recency status, coverage counts, and metric-specific 1/5/10-year changes. Missing-year rows are materialized for all cohort entities.

Coverage schema `1.1` contains the complete country × metric matrix, including never-observed pairs. Inventory fields distinguish `ever_observed_country_count` from `ranking_year_observed_country_count`; clients must not substitute one for the other.
