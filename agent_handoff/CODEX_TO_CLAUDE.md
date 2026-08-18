# Codex → Claude review queue

## Implementation ID

GEI-D001

## Feature

Top-50 universe construction

## Source Used

World Bank WDI `NY.GDP.MKTP.CD`

## Data Availability

Broad annual country coverage; newest year may be incomplete.

## Observed Problem

“Sufficiently complete” was not numerically defined.

## Engineering Decision

Use the latest year with at least 150 non-aggregate economy observations, then rank the first 50.

## Potential Economic Impact

The threshold can select a slightly older year and may include separately reported territories.

## Questions for Economic Review

Should the eligibility universe use UN members only, World Bank economies, or a documented sovereignty list? Is 150 observations the right completeness threshold?

## Files Changed

`gei/pipeline.py`, `docs/METHODOLOGY.md`

## Tests Added

Payload uniqueness and universe-size contract.

---

## Implementation ID

GEI-D003

## Feature

Configuration-driven metric and source selection

## Source Used

Existing Phase 1 World Bank WDI mappings only; no new economic sources or indicators were introduced.

## Data Availability

Unchanged from the existing seven-metric Phase 1 snapshot.

## Observed Problem

Economic labels, source mappings, units, formatting, and transformations were duplicated in Python and frontend code, making methodological changes structurally expensive.

## Engineering Decision

Create a canonical versioned metric registry with declarative source, display, unit, transformation, missing-data, directionality, chart, and availability fields. `directionality` remains `not_assessed`; freshness rules remain null.

## Potential Economic Impact

None intended. Existing economic definitions and caveats were preserved verbatim or equivalently restated; no favorable/unfavorable semantics were added.

## Questions for Economic Review

Please edit or approve registry descriptions, units, directionality, missing-data policies, and any future source remapping. These are now configuration changes.

## Files Changed

`config/metrics.json`, `gei/config.py`, `gei/pipeline.py`, `app/app.js`, `docs/ADDING_A_METRIC.md`

## Tests Added

Registry schema, duplicate ID, required-field, and malformed transformation tests.

---

## Implementation ID

GEI-D004

## Feature

Observation-year and freshness infrastructure

## Source Used

Existing Phase 1 sources.

## Data Availability

Each observation now carries `reference_period`, `retrieved_at`, raw snapshot lineage, and pipeline-run lineage.

## Observed Problem

The application needs a future reviewed freshness classification without hard-coded engineering thresholds.

## Engineering Decision

Expose reference period and retrieval timestamp structurally, set `meta.freshness_rules` to null, and retain explicit observation years throughout the UI and enriched export.

## Potential Economic Impact

No freshness judgment is currently produced.

## Questions for Economic Review

Please define any freshness-status vocabulary and per-frequency threshold rules before the UI displays a status label.

## Files Changed

`gei/schemas.py`, `gei/pipeline.py`, `app/app.js`, `docs/DATA_CONTRACTS.md`

## Tests Added

Provenance propagation, stable observation identity, missing provenance, invalid period, and deterministic pipeline tests.

---

## Implementation ID

GEI-D005

## Feature

Data release, snapshot diff, regression, and coverage infrastructure

## Source Used

Existing Phase 1 sources and mappings only.

## Data Availability

The current formal release contains 11,308 Top-50 observations. The retained previous formal release also contained 11,308; their generated diff reports zero additions, removals, or revisions.

## Observed Problem

The earlier reported 12,600 → 11,308 count change predates formal release snapshots, so it cannot be reconstructed reliably from a complete old/new canonical pair. Future changes are now automatically attributable.

## Engineering Decision

Create content-derived release IDs, versioned release manifests, raw/registry/code fingerprints, configurable non-economic regression gates, and machine/Markdown diffs with absolute and percent revisions. Emit coverage matrices without quality interpretation.

## Potential Economic Impact

None intended. Revision materiality thresholds default to zero for reporting and are configurable; ordinary revisions are non-blocking.

## Questions for Economic Review

Claude may later define reviewed alert thresholds or coverage interpretation. Current regression severities are structural operations policy only.

## Files Changed

`gei/diff.py`, `gei/release.py`, `gei/regression.py`, `gei/coverage.py`, `config/regression_rules.json`, `data/releases/`, `data/diffs/`

## Tests Added

Diff math and outputs, release determinism, regression blocking semantics, and coverage-grain tests.

---

## Implementation ID

GEI-D006

## Feature

Catalog-first lazy frontend and URL state

## Source Used

Registry metadata and versioned static metric shards.

## Data Availability

Initial catalog is approximately 19 KB. Overview loads only the three declared overview metric shards; other metrics load on demand.

## Observed Problem

The monolithic analytical payload duplicates all metric data at initial load and would become untenable near 100 metrics.

## Engineering Decision

Implement on-demand shard loading, in-memory cache/request deduplication, retryable failures, URL allowlisting, centralized formatting, and query-state reproduction. Keep the monolith only as backward-compatible fallback.

## Potential Economic Impact

None. The same canonical observations and registry metadata drive rendering.

## Questions for Economic Review

None; final public labels and methodology copy remain Claude-reviewable through registries and documentation.

## Files Changed

`app/app.js`, `app/index.html`, `app/styles.css`, `scripts/build_static.py`, `docs/DEPLOYMENT.md`

## Tests Added

Static syntax/build validation and browser QA for lazy loading, shard selection, URL state, and failure-free rendering.

---

## Implementation ID

GEI-D002

## Feature

Government debt burden

## Source Used

World Bank WDI `GC.DOD.TOTL.GD.ZS`

## Data Availability

Sparse and uneven across the Top 50.

## Observed Problem

The indicator measures central-government debt, whereas the specification asks broadly for government debt/GDP and users may expect IMF general-government gross debt.

## Engineering Decision

Keep the series provisionally, label it “Central government debt,” display missingness, and publish the scope caveat beside the metric definition.

## Potential Economic Impact

Cross-country ranks may reflect institutional scope rather than fiscal burden.

## Questions for Economic Review

Approve replacing this with IMF WEO general-government gross debt in the next adapter iteration?

## Files Changed

`gei/config.py`, `gei/pipeline.py`, `app/app.js`

## Tests Added

Provenance and raw/display-value integrity checks.

---

# AUDIT SUPPORT PACKAGE

The evidence-only package for the current published release is indexed at `docs/audit/README.md`.

Release binding:

- Release ID: `release_e9182edbdb3e275e19ca`
- Pipeline run ID: `run_9c142b7be97fd869979dd671`
- Git commit recorded by the release: `284bae0a22a636e072be057c3bab35efd19969e4`
- Machine-readable bundle: `data/audit/release_e9182edbdb3e275e19ca/`

Audit reports:

- `docs/audit/CURRENT_METRIC_INVENTORY.md`
- `docs/audit/COUNTRY_YEAR_FRESHNESS.md`
- `docs/audit/TOP50_UNIVERSE_EVIDENCE.md`
- `docs/audit/LINEAGE_EXAMPLES.md`
- `docs/audit/MISSING_DATA_SUMMARY.md`
- `docs/audit/CURRENT_DEBT_IMPLEMENTATION.md`
- `docs/audit/CURRENT_INFLATION_IMPLEMENTATION.md`
- `docs/audit/CURRENT_UNEMPLOYMENT_IMPLEMENTATION.md`
- `docs/audit/CURRENT_GDP_IMPLEMENTATION.md`
- `docs/audit/CURRENT_RANKING_IMPLEMENTATION.md`
- `docs/audit/UI_ECONOMIC_METADATA.md`
- `docs/audit/TEST_COVERAGE_MAP.md`

The package was generated from the published payload, its referenced raw snapshots, current registries, rejection file, implementation, and tests. It does not change metrics, sources, transformations, ranking behavior, missing-data policy, or UI behavior.
