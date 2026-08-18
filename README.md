# Atlas — Global Economic Intelligence

Atlas is a source-traceable Phase 1 comparison product for the world's 50 largest economies. It separates published observations from transformations and presentation, preserves raw API responses, and exposes observation year, indicator code, source, retrieval date, coverage, and caveats in the interface.

## Phase 1 capabilities

- Reproducible Top-50 universe based on nominal GDP in the latest sufficiently complete common year
- Seven declaratively registered World Bank WDI indicators: GDP, GDP per capita, real GDP growth, population, CPI inflation, unemployment, and central-government debt/GDP
- Overview, rankings, indexed country comparison, country profiles, data explorer, CSV export, and methodology
- Raw-response preservation, stable lineage identifiers, normalized country-year observations, rejected-record output, and historical run manifests
- Content-derived data releases, build-to-build snapshot diffs, configurable regression gates, and three-grain coverage matrices
- Visible missingness and per-country latest-year logic
- Structural validation plus unit/integration/data-quality tests for adapters, caching, normalization, lineage, determinism, transformations, and payload integrity

## Installation

Requires Python 3.11+; the application itself has no package dependencies.

```bash
git clone https://github.com/jsaintfleur/global-economic-intelligence.git
cd global-economic-intelligence
python3 --version
```

No package installation is required for the Phase 1 static application or its standard-library Python pipeline.

## Local development

Serve the checked-in application payload locally:

```bash
python -m http.server 8080 --directory app
```

Open `http://localhost:8080`.

## Data pipeline

The production pipeline retrieves World Bank WDI data, preserves immutable dated raw snapshots, normalizes source records, selects the GDP universe, validates observations, and writes release-bound application assets:

```bash
python -m gei.pipeline
```

This command requires network access for a new source refresh. To exercise the pipeline without changing the published production release or using the network:

```bash
make data-fixture
```

The alternate snapshot builder can be rerun after a successful refresh with `python -m pipelines.build --from-cache` and is retained for compatibility; the production implementation is `gei.pipeline`.

## Testing and validation

Run the same structural checks used before publication:

```bash
make check
make test
make data-fixture
make inventory
python -m unittest tests.data_quality.test_production_payload -v
```

The current suite contains 37 tests spanning source contracts, normalization, lineage, transformations, releases, coverage, configuration, and production-payload integrity. The Phase 1.1 audit identifies that legacy universe tests must be moved onto the production `gei.pipeline` selection path.

## Production build

Create the deployable static package:

```bash
make build
```

The build validates Python, frontend JavaScript, registries, and configuration before writing the static site to `dist/`. `dist/` is generated and intentionally excluded from Git; deployment systems should run the repository build rather than treat local output as source.

## Repository map

```text
app/                 Static interactive application
  data/              Runtime dashboard payload
gei/                 Adapters, schemas, transformations, pipeline
data/raw/            Immutable source responses by retrieval date
data/processed/      Canonical JSON and CSV outputs
data/manifests/      Machine-readable history of pipeline attempts
data/releases/       Release manifests and local snapshot archive
data/diffs/          Machine-readable and Markdown release comparisons
tests/               Unit and data-contract tests
docs/                Architecture and methodology
agent_handoff/       Structured Claude ↔ Codex interface
```

The application is deliberately static at runtime. `app/data/catalog.json` loads first, and versioned metric shards under `app/data/metrics/` load on demand. See `docs/ARCHITECTURE.md` and `docs/DEPLOYMENT.md` for the complete design and hosting contract.

## Sources, provenance, and releases

Phase 1 uses declaratively registered World Bank World Development Indicators. Every accepted observation retains its source, dataset, indicator, retrieval timestamp, raw snapshot ID, raw record index, transformation ID, pipeline run, and stable observation ID. Raw responses are preserved by retrieval date and SHA-256; release manifests bind application data to source snapshots, registries, code commit, and validation status.

The project does not interpolate missing observations or present modeled values as published facts. See `docs/METHODOLOGY.md`, `docs/RAW_DATA_POLICY.md`, and `docs/DATA_CONTRACTS.md`.

## Refresh behavior

The pipeline downloads broad World Bank datasets for all non-aggregate economies before selecting the Top 50. A refresh may therefore change the universe when a newer sufficiently complete GDP year appears. Raw snapshots are date-partitioned; processed outputs are replaced by the latest successful build.

Metrics are defined in `config/metrics.json`. See `docs/ADDING_A_METRIC.md`, `docs/ADDING_AN_ADAPTER.md`, and `docs/DATA_CONTRACTS.md` for extension contracts. The app build also emits per-metric observation shards so a future lazy-loading frontend can avoid shipping the full panel at 100–200 metric scale.

The frontend now consumes those shards directly: it loads the catalog first, fetches overview essentials, then loads additional metrics on demand with request deduplication, in-memory caching, failure/retry states, and shareable query-string state.

## Current limitations

WDI's central-government debt indicator is materially sparse and is not equivalent to general-government gross debt. In the current release, 35 of 50 economies have any historical debt observation, but only 15 have an observation in the metric's latest year, 2024. The static frontend reads a published snapshot, not a live API connection.

Current non-GDP metric rankings use each country's latest available value and can therefore compare different observation years. The common-year GDP universe is internally consistent for entities present in the World Bank source, but that source omits some candidate entities, including Taiwan. Territory/analytical eligibility is not inferred; the current registry leaves classification null.

## Phase 1.1 audit status

Phase 1 is implemented and release-audited. Phase 1.1 is specified but not yet implemented. Its approved work includes common-year metric ranking, explicit observation-recency metadata, production-path universe tests, and an economist-reviewed analytical-entity eligibility registry. Start with `docs/audit/README.md` and `agent_handoff/CLAUDE_TO_CODEX.md`. No Phase 2 forecasting, scoring, or additional economic methodology is part of the current release.
