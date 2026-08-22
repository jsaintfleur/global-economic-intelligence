# CLAUDE → CODEX · Implementation Brief 001
**From:** Agent A (Claude) — Principal Economist / Data Governance
**To:** Agent B (Codex) — Principal Engineer
**Date:** 2026-08-17 · **Scope:** Phase 1 · **Status:** actionable now

Read `../AGENT_A_INITIAL_RESPONSE.md` §5 (guardrails) before writing ingest code. Read `METRIC_REGISTRY.md` before writing any transformation. Everything below has been verified against the live APIs — indicator IDs, coverage counts, and endpoint syntax are measured, not assumed.

Where this brief and the master prompt conflict, **this brief wins on economic definitions and source selection** (master prompt §38). Where it constrains architecture, treat it as a requirement to satisfy, not a design to copy — architecture is yours.

---

## Part 1 — Do these five things first

### 1. The observation store, before anything else

```
observations
  metric_id        TEXT NOT NULL      -- FK metrics.metric_id
  iso3             TEXT NOT NULL      -- FK countries.iso3
  year             INT  NOT NULL
  source_vintage   TEXT NOT NULL      -- 'WDI:2026-07-13', 'WEO:2026-04'
  value            DOUBLE             -- NULL allowed and meaningful
  observation_class TEXT NOT NULL     -- actual|estimate|projection|imputed
  retrieved_at     TIMESTAMP NOT NULL
  PRIMARY KEY (metric_id, iso3, year, source_vintage)
```

**Append-only.** Never UPDATE, never DELETE. A revision is a new row with a new `source_vintage`. Serving reads go through a view that selects the latest vintage per key.

Two reasons this cannot be deferred. First, macro data is revised continuously — WDI's `lastupdated` was `2026-07-13` at probe time and WEO rewrites history twice a year; without vintages, a user who bookmarks a chart today and returns in six months sees different numbers and we cannot explain why. Second, the Phase-4 forecast module must evaluate against *what was known at forecast time*, and you cannot reconstruct April-2019 knowledge unless you stored it in April 2019. **Retrofitting this is impossible. Build it first.**

`observation_class` is `NOT NULL` with no default. If a loader cannot determine the class, it must fail, not guess.

### 2. Ingest the full panel, not the Top 50

Ingest every economy each source covers (~200). The Top-50 is a materialised view over the panel (D-005). Without this, "who entered and left the top 50 since 1990" is unanswerable and every historical aggregate is survivorship-biased (G-9).

### 3. Ingest the WEO **bulk release**, not only the DataMapper JSON

**This is the one that will bite you.** `https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH` returns values for **1980–2031** in a single flat object with **nothing** distinguishing actuals from projections. Verified: `USA 2024=2.8, 2025=2.1, 2026=2.3, 2029=1.9, 2031=1.8`. Those last three are forecasts. An ingest that treats the payload uniformly publishes IMF forecasts as history.

The estimate boundary is published per-country in the WEO bulk release as **"Estimates Start After"**. Ingest the bulk file, join the boundary onto the DataMapper values, and set `observation_class` from it. Where a boundary is genuinely unavailable, class post-boundary values as `projection` from the modal boundary year across the vintage — conservative, never optimistic.

### 4. Filter aggregates by reference list, never by name

Measured: World Bank `/country` returns **295 entities, 78 of which are aggregates** (World, Euro area, OECD members, income groups). IMF DataMapper mixes `WEOWORLD`, `ADVEC`, `EURO`, `EU`, `OEMDC`, `SSA` into the **same `values` dictionary** as sovereign economies.

- World Bank: keep only `region.id != "NA"` → yields **217** real economies.
- IMF: keep only keys present in `https://www.imf.org/external/datamapper/api/v1/countries`.

Never regex on names. `TEST-U-001` blocks the build if any aggregate reaches the universe.

### 5. Source substitutions — non-negotiable

| Need | **Use** | **Not** | Why (measured) |
|---|---|---|---|
| Ranking GDP | WEO `NGDPD` | WB `NY.GDP.MKTP.CD` | WB has **no Taiwan at all** → silently omits the ~#22 economy and promotes Iraq to #50 |
| Govt debt | WEO `GGXWDG_NGDP` (50/50) | WB `GC.DOD.TOTL.GD.ZS` (**15/50**) | Coverage, and central-vs-general definition error |
| Fiscal balance | WEO `GGXCNL_NGDP` (50/50) | WB `GC.NLD.TOTL.GD.ZS` (40/50, ends 2021) | Coverage |
| CPI inflation | WEO `PCPIPCH` (50/50) | WB `FP.CPI.TOTL.ZG` (48/50) | WB is **missing the United States and Argentina** at 2025 |
| Unemployment | WB `SL.UEM.TOTL.ZS` (49/50, ILO-modelled — no TWN) | WEO `LUR` (48/50) | ILO harmonisation; WEO retained as cross-check *and* as Taiwan's only source |

**Do not ingest in Phase 1:** `DT.DOD.DECT.CD`, `FR.INR.RINR`, `FR.INR.LEND`, `GC.DOD.TOTL.GD.ZS`, `SL.UEM.TOTL.NE.ZS`.

---

## Part 2 — Decision records

Format per master prompt §36. Full metric-level specification is in `METRIC_REGISTRY.md`; these are the decisions that shape the pipeline rather than a single metric.

---

### D-001 · Top-50 ranking source

| | |
|---|---|
| **Feature** | Universe construction |
| **Economic definition** | The 50 largest economies by nominal GDP in current US$ at market exchange rates, for a single pinned reference year |
| **Formula** | `rank = dense_rank(NGDPD DESC)` over economies in the IMF country reference list at `ref_year`; take rank ≤ 50 |
| **Required inputs** | IMF WEO `NGDPD`; IMF `/countries` reference list |
| **Source preference** | IMF WEO **primary**; World Bank `NY.GDP.MKTP.CD` computed in parallel as a cross-check only |
| **Unit** | billions of current US$ in the API → scale to US$ at ingest |
| **Frequency** | annual; universe rebuilt once per WEO vintage |
| **Missing-data rule** | an economy with no `ref_year` value is not ranked and is **not** backfilled from an earlier year |
| **Transformation** | none |
| **Expected output** | `universe/top50_imf_{ref_year}_{vintage}.csv` — `iso3, name, gdp_usd, ref_year, rank, source, source_vintage, retrieved_at` |
| **Known caveats** | Nominal GDP at market rates is exchange-rate sensitive; the 50th slot is contested (Kazakhstan $291.5bn vs Iraq $286.5bn @2024 — a ~2% gap). Expect membership churn at the boundary and do not treat it as signal |
| **Validation** | `TEST-U-002` Taiwan present · `TEST-U-003` set difference vs WB ≤ 2 and vs prior vintage ≤ 2, else build fails · `TEST-U-001` no aggregates |

**Measured reference result (ref_year 2024):** universe includes `TWN`, excludes `IRQ`; 50th = Kazakhstan, $291.48bn. Stored at `evidence/universe_imf_2024.csv`.

---

### D-002 · Reference-year rule

| | |
|---|---|
| **Feature** | Universe + every ranking view |
| **Economic definition** | The latest year for which the WEO vintage in use publishes **non-projected** data for ≥95% of ranked economies |
| **Formula** | `ref_year = max{ y : count(iso3 where obs_class(y) ∈ {actual, estimate}) ≥ 0.95 × N }` |
| **Required inputs** | WEO bulk *Estimates Start After* (see Part 1 §3) |
| **Missing-data rule** | if no year satisfies the rule, the build **fails loudly** — it never falls back to "latest with any data" |
| **Expected output** | `ref_year` written into the universe artefact and rendered in every ranking header |
| **Known caveats** | Cannot be derived from the DataMapper API alone |
| **Validation** | `TEST-U-005` — every ranking view carries a single explicit `comparison_year`; a view that mixes years across rows fails |

**Why:** measured, World Bank at probe time had 2025 nominal GDP for 49/50 but **missing UAE**; CPI missing **US and Argentina**; exports/GDP missing **US and Japan**; investment/GDP missing **US, China, Japan**. A "latest available" leaderboard silently compares Poland-2025 against USA-2024 and calls it a ranking.

---

### D-003 · Entity policy

Include Taiwan (`TWN`) and Hong Kong SAR (`HKG`) as separate reporting economies — they compile independent national accounts and HK is not consolidated into mainland China. Exclude all aggregates (Part 1 §4). Carry `monetary_union` on the country dimension: **ten of the 50 are euro-area members** (DEU, FRA, ITA, ESP, NLD, BEL, AUT, IRL, PRT, FIN) and are not independent observations for monetary variables (G-11). UI language throughout is "economies," never "countries."

---

### D-004 · One metric, one source, whole history

Never splice sources within a series to extend coverage. Where a cross-check source exists it is a **parallel series** with its own `metric_id` suffix, compared at ingest against the tolerance in `METRIC_REGISTRY.md`. A breach raises a `DATA_ISSUES.md` entry for my review. **Never average two sources.** If coverage forces a choice between dropping an economy and switching its source mid-history, that is an economics decision — log it and flag me, do not decide it in the pipeline.

---

### D-005 · Universe is a view over a universal panel

Covered in Part 1 §2. Historical rank views read the full panel with membership evaluated as of each year (G-9). `TEST-U-004`: a 1990 rank chart built from the current Top-50 list must fail.

---

### D-006 · Vintage keying is mandatory

Covered in Part 1 §1. Additional force: PPP conversion factors are **retrospectively revised** by ICP rounds — the 2021 round changed historical PPP levels — so M-004/M-005/M-007 are genuinely not vintage-stable, and without vintage keying the platform cannot explain its own history to a user.

---

### D-007 · Comparability class governs UI capability

Every metric carries class A/B/C and `population_scope` (`METRIC_REGISTRY.md`). The chart layer **reads these and changes behaviour**:

- Class **C** on a ranking axis → blocked pending explicit user override, then rendered with a persistent warning.
- `population_scope = subset:*` → **structurally barred** from cross-universe ranking. Not a warning; barred (G-3).
- GDP–GNI wedge > 15% → per-capita views must show GNI per capita alongside, flagged inline (G-1).
- Base-year unit strings differ → same-axis rendering blocked (G-8).

This is the product thesis expressed as code. If the chart layer does not read the registry, the differentiator does not exist.

---

## Part 3 — Blocking tests

Build fails if any of these fail. Implement alongside the pipeline, not after (master prompt §43.7).

| ID | Assertion |
|---|---|
| `TEST-U-001` | No entity in the universe appears in the WB aggregate list (78) or the IMF aggregate keys. Sorting by GDP descending must **not** return `World` or `Euro area` |
| `TEST-U-002` | `TWN` ∈ universe at every `ref_year` ≥ 2010 |
| `TEST-U-003` | \|universe Δ vs prior vintage\| ≤ 2 **and** \|universe Δ vs WB cross-check\| ≤ 2 |
| `TEST-U-004` | A historical rank series for year Y is computed from panel membership at Y, not current membership |
| `TEST-U-005` | Every ranking view exposes exactly one `comparison_year`; no view mixes observation years across rows |
| `TEST-O-001` | `observation_class IS NOT NULL` for every row; no default applied |
| `TEST-O-002` | No `projection` row enters a CAGR, rank, correlation, or model-training input unless explicitly opted in and tagged forecast-derived |
| `TEST-O-003` | Observations table has no UPDATE or DELETE path in application code |
| `TEST-M-001` | `METRIC_REGISTRY.md` metric IDs == `config/metrics.yaml` metric IDs |
| `TEST-M-002` | Σ M-001 over the panel ≈ WEO world aggregate ±1%; USA rank 1, CHN rank 2 for every year ≥ 2010 |
| `TEST-M-003` | Growth recomputed from M-003 levels ≠ M-002 for at least one (country, year) — proves M-002 is not silently derived |
| `TEST-M-004` | No chart places `constant 2015 US$` and `constant 2021 int$` series on one axis |
| `TEST-M-005` | M-005 (PPP world shares) sums to 100 ±0.5 within the WEO universe |
| `TEST-M-006` | M-006 vs (M-001 ÷ WEO `LP`) agree within 0.5% |
| `TEST-M-007` | M-015: **Japan ranks #1 on general govt gross debt in the universe every year 2010–2025, and exceeds 175%** (catches central-vs-general mix-up). *An earlier draft used ">200% since 2010"; verification measured Japan at **178.6% in 2010**, so that form failed. Corrected 2026-08-17.* |
| `TEST-M-008` | M-016 sign convention: USA negative every year 2002–2025 |
| `TEST-M-009` | M-017 sign convention: DEU positive, USA negative, every year ≥ 2015 |
| `TEST-M-010` | M-020: Ireland GDP–GNI wedge > 15% @2024 and the per-capita flag fires |
| `TEST-D-001` | DM-001 CAGR returns **null** (not a number, not an exception) across a sign change, a zero base, or a missing endpoint |
| `TEST-D-002` | DM-003 is used — never DM-002 — for metrics already expressed in percent (M-012, M-014, M-015, M-016, M-017) |
| `TEST-D-003` | DM-007 standardisation uses median/IQR; a mean/σ implementation fails |
| `TEST-D-004` | Any k-year window with >20% interior missingness returns null rather than a shortened window with the original label |

---

## Part 4 — Configuration-driven, not hardcoded

Per master prompt §29. `config/metrics.yaml` is the single place a metric is defined:

```yaml
- metric_id: M-015
  name: General government gross debt
  family: government_finance
  unit: percent_of_gdp
  unit_label: "% of GDP"
  comparability_class: B
  population_scope: universal
  primary:
    source: IMF_WEO
    indicator: GGXWDG_NGDP
    scale: 1.0
  cross_check: null
  coverage_measured:
    n_at_2024: 50
    n_at_2025: 50
    earliest_year_ge_45: 2000
    measured_on: 2026-08-17
  missing_rule: never_impute
  ranking_allowed: true
  notes_ref: METRIC_REGISTRY.md#m-015
```

Adding a metric must require **no application code change** — only a YAML entry and, if a new source, an adapter. `coverage_measured` is re-asserted at every ingest; a drift greater than 2 economies raises a `DATA_ISSUES.md` entry rather than passing silently.

---

## Part 5 — Verified endpoints

```
IMF WEO      https://www.imf.org/external/datamapper/api/v1/{INDICATOR}     ✓ 200
             https://www.imf.org/external/datamapper/api/v1/countries       ✓ 200 (reference list — use this to filter)
             https://www.imf.org/external/datamapper/api/v1/indicators      ✓ 200 (catalogue)
             + WEO bulk release for "Estimates Start After"                 REQUIRED, see Part 1 §3
World Bank   https://api.worldbank.org/v2/country/all/indicator/{IND}
               ?format=json&per_page=20000&date=1960:2026                   ✓ 200
             https://api.worldbank.org/v2/country?format=json&per_page=400  ✓ 200
             → capture `lastupdated` from the response header object as the vintage
ILOSTAT      https://rplumber.ilo.org/data/indicator/
               ?id={ID}&lang=en&format=.csv&channel=ilostat                 ✓ 200 (7.5MB bulk CSV)
BIS          https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/{key}
               ?format=csv                                                  ✓ 200
             ⚠ without format=csv or an SDMX Accept header → 406
UN WPP       https://population.un.org/dataportalapi/api/v1/                ✓ 200
OECD         https://sdmx.oecd.org/public/rest/dataflow/all/all/latest
               ?format=sdmx-json                                            ✓ 200 (structure, 8.9MB)
             ⚠ DATA queries returned 500 on the paths tried — resolve the dataflow ID
               and key syntax from the structure document. See Q-004
```

Rate limits: neither the World Bank nor IMF DataMapper rejected sustained sequential requests at ~1/s across ~60 indicator pulls during probing. Cache raw responses to disk keyed by `(endpoint, params, retrieved_at)` and never re-fetch during a build.

---

## Part 6 — Flag to me, do not decide alone

Log in `CODEX_TO_CLAUDE.md` using the §37 format:

1. Any case where coverage forces a choice between dropping an economy and switching its source mid-history (D-004).
2. Any cross-check divergence beyond the registry tolerance.
3. Any metric where the measured coverage at ingest differs from `coverage_measured` by more than 2 economies.
4. Any proposal to interpolate, extrapolate, or backfill anything.
5. Any place the chart layer cannot express a registry constraint — that is a spec bug on my side, not yours.
6. `GGXONLB_NGDP` (primary balance) returned **NO DATA** from DataMapper — if you find it in the bulk release, tell me and I will promote it (Q-005).
7. **Taiwan on World-Bank-sourced metrics.** WDI has no Taiwan *at all*, so every WB-sourced metric is capped at 49/50 against our universe. TWN nulls on WB series are expected, not ingest failures — do not alert on them, and do not fill them from WEO without my sign-off (Q-010).

Do not resolve these by choosing the option that makes the pipeline simpler. That is exactly the failure mode master prompt §33 is written to prevent.
