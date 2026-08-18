# Atlas — Global Economic Intelligence

[![CI](https://github.com/jsaintfleur/global-economic-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/jsaintfleur/global-economic-intelligence/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Data source: World Bank WDI](https://img.shields.io/badge/Data-World%20Bank%20WDI-0071BC)](https://databank.worldbank.org/source/world-development-indicators)

Atlas is an open-source economic intelligence platform for exploring and comparing the world’s largest economies with reproducible, source-backed macroeconomic data.

The project combines a dependency-free static web application with a deterministic Python data pipeline. Every published observation retains its source indicator, observation year, retrieval timestamp, raw snapshot, transformation, pipeline run, and stable lineage identifier.

> **Project status:** Phase 1.1 is implemented and undergoing review on its feature branch. It hardens analytical-entity eligibility, exact-year rankings, observation recency, coverage disclosure, and production UX. Atlas does not include forecasting, scoring, or machine-learning features.

## What Atlas provides

- A reproducible Top-50 economy universe based on nominal GDP in a common reference year
- A GDP treemap, common-year macroeconomic overview, rankings, and distribution context
- Hierarchical economy profiles with deterministic Data Highlights and rank history
- Multi-country comparison in absolute, indexed, rank, and change modes
- A common-year scatter explorer with optional GDP or population bubble encoding
- Interactive historical charts and lineage-rich downloadable CSV exports
- A keyboard-accessible global command search (`⌘ K` / `Ctrl K`)
- Purpose-designed light and dark themes with responsive analytical layouts
- Shareable URL state for metrics, countries, and year ranges
- Lazy-loaded, release-versioned metric shards for efficient static delivery
- Explicit observation years, missing-data states, source codes, coverage, and caveats
- Immutable raw-source snapshots, stable lineage IDs, release manifests, and snapshot diffs
- Configuration-driven metric, source, country, transformation, and regression registries
- Unit, integration, contract, data-quality, and production-payload validation

## Phase 1 metrics

| Metric | World Bank indicator | Unit |
| --- | --- | --- |
| Nominal GDP | `NY.GDP.MKTP.CD` | Current US$ |
| GDP per capita | `NY.GDP.PCAP.CD` | Current US$ per person |
| Real GDP growth | `NY.GDP.MKTP.KD.ZG` | Annual % change |
| Population | `SP.POP.TOTL` | People |
| CPI inflation | `FP.CPI.TOTL.ZG` | Annual % change |
| Unemployment | `SL.UEM.TOTL.ZS` | % of labor force, modeled ILO estimate |
| Central-government debt | `GC.DOD.TOTL.GD.ZS` | % of GDP |

Metric definitions, display metadata, transformations, and caveats are declared in [`config/metrics.json`](config/metrics.json). Phase 1 uses identity transformations for all seven published series and does not interpolate missing observations.

## Quick start

### Requirements

- Python 3.11 or newer
- Node.js for the frontend syntax check
- A modern web browser
- `make` for the documented convenience commands

The application and production pipeline otherwise use the Python standard library and browser-native JavaScript—there are no runtime package dependencies to install.

### Clone and run locally

```bash
git clone https://github.com/jsaintfleur/global-economic-intelligence.git
cd global-economic-intelligence
make app
```

Open [http://localhost:8765](http://localhost:8765).

The checked-in application assets contain the validated current release, so a network data refresh is not required for local exploration.

## Validation

Run the complete local validation sequence:

```bash
make check
make test
python3 -m unittest tests.data_quality.test_production_payload -v
make data-fixture
make inventory
make build
```

| Command | Purpose |
| --- | --- |
| `make check` | Compile Python, check frontend JavaScript, validate JSON and registries |
| `make test` | Run the complete unit, integration, contract, and data-quality suite |
| `make data-fixture` | Exercise the pipeline deterministically without network access |
| `make inventory` | Print current metric coverage and observation counts |
| `make audit` | Regenerate the release-bound economic audit package |
| `make build` | Validate and create the deployable static package in `dist/` |

GitHub Actions runs configuration checks, all tests, production-payload validation, and the static production build on pushes and pull requests.

## Production data pipeline

Run a new World Bank refresh with:

```bash
make data
```

The production path is `gei.pipeline`. A successful run:

1. Retrieves the World Bank country dimension and registered indicators.
2. Preserves immutable, date-partitioned raw responses with SHA-256 checksums.
3. Normalizes source records into canonical country–metric–year observations.
4. Records rejected records and structural rejection reasons.
5. Selects the configured GDP universe and validates the Top-50 panel.
6. Produces coverage matrices, release manifests, regression results, and diffs.
7. Writes the static application catalog and per-metric data shards.

A refresh requires network access and may change the selected universe when a newer sufficiently complete GDP year becomes available. Use `make data-fixture` when you only need a safe, offline pipeline check.

The legacy-compatible cache builder remains available as `python3 -m pipelines.build --from-cache`; it is not the current production pipeline.

## Architecture

```text
World Bank WDI
      │
      ▼
Source adapters ──► immutable raw snapshots
      │
      ▼
Normalization ──► canonical observations + rejected records
      │
      ▼
Registries and validation ──► universe, coverage, releases, diffs
      │
      ▼
Static catalog + metric shards ──► Atlas web application
```

| Path | Responsibility |
| --- | --- |
| `app/` | Dependency-free HTML, CSS, JavaScript, and published runtime data |
| `gei/` | Production adapters, normalization, validation, releases, and pipeline |
| `config/` | Versioned metric, source, country, transformation, and regression registries |
| `data/raw/` | Immutable source responses, excluded from Git except for `.gitkeep` |
| `data/processed/` | Canonical local pipeline outputs, excluded from Git |
| `data/manifests/` | Pipeline-run history and source snapshot references |
| `data/releases/` | Versioned release manifests and regression reports |
| `data/audit/` | Machine-readable release audit evidence |
| `docs/audit/` | Human-readable economic and implementation audit reports |
| `tests/` | Unit, integration, source-contract, and production data-quality tests |
| `agent_handoff/` | Structured methodology and implementation decisions |

For more detail, see [Architecture](docs/ARCHITECTURE.md), [Data contracts](docs/DATA_CONTRACTS.md), and [Schema versioning](docs/SCHEMA_VERSIONING.md).

Frontend performance budgets are documented in [Performance budgets](docs/PERFORMANCE_BUDGETS.md). Deterministic desktop, tablet, mobile, and dark-mode review captures are indexed in [Visual QA](docs/VISUAL_QA.md).

## Provenance and release philosophy

Atlas treats provenance as part of the data model rather than supplemental documentation. Every accepted observation carries:

- source and dataset identifiers
- the authoritative indicator code
- observation and retrieval dates
- raw snapshot ID and raw record index
- raw, transformed, and modeled value fields
- transformation and pipeline-run identifiers
- a deterministic observation ID

Successful releases bind application data to raw snapshots, registry fingerprints, source-adapter versions, validation status, and the recorded Git commit. Routine refreshes never overwrite raw evidence.

See [Raw data policy](docs/RAW_DATA_POLICY.md), [Operations](docs/OPERATIONS.md), and the [current audit bundle](docs/audit/README.md).

## Methodology and known limitations

Atlas is explicit about the current release’s methodological boundaries:

- **Exact-year rankings:** every ranking uses one declared year. Missing entities remain visible but unranked; older observations appear only as separately labelled context.
- **Debt coverage:** the World Bank central-government debt series is not general-government gross debt. In the current release, 35 of 50 economies have any historical observation, while 15 have an observation in the series’ latest year, 2024.
- **Candidate-universe completeness:** Top-50 GDP values use a common 2025 observation year for entities available in the World Bank source. That source omits some analytical candidates, including Taiwan, so same-year consistency does not establish global candidate completeness.
- **Entity eligibility:** sovereignty or territory status is not inferred programmatically. A versioned analytical-entity registry records explicit eligibility and authoritative identifiers; Taiwan remains pending review until an approved GDP provider mapping is adopted.
- **Static release:** the browser reads a published snapshot, not a live World Bank connection.

Read the complete [Phase 1 methodology](docs/METHODOLOGY.md), [Phase 1.1 audit findings](docs/audit/PHASE_1_1_FINDINGS.md), and [implementation specification](agent_handoff/CLAUDE_TO_CODEX.md).

## Building and deployment

Create the production package with:

```bash
make build
```

The generated `dist/` directory contains the complete static application plus a build manifest with asset sizes and SHA-256 checksums. It is intentionally excluded from Git; deployment systems should run the repository build and publish `dist/`.

No server runtime, application secret, API key, database, or rewrite layer is required. See [Deployment](docs/DEPLOYMENT.md) for caching and 404 behavior.

## Extending Atlas

- [Adding a metric](docs/ADDING_A_METRIC.md)
- [Adding a source adapter](docs/ADDING_AN_ADAPTER.md)
- [Change classification](docs/CHANGE_TYPES.md)
- [Phase 2 readiness](docs/PHASE_2_READINESS.md)

Economic definitions, source substitutions, entity eligibility, and freshness thresholds require explicit review. Engineering changes should preserve raw evidence, lineage, missingness, and release reproducibility.

## Current release

- Release: `release_c95979a1f2a0d628fbf3`
- Pipeline run: `run_9c142b7be97fd869979dd671`
- Universe: 50 economies
- Metrics: 7
- Observations: 11,308
- Reference year: 2025
- Validation status: passed

Release fingerprints and audit navigation are available in [`docs/audit/README.md`](docs/audit/README.md).
