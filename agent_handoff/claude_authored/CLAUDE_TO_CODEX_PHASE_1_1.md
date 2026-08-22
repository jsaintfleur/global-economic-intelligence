# CLAUDE → CODEX · Phase 1.1 Specification
**From:** Agent A (Claude) — Principal Economist / Data Governance
**To:** Agent B (Codex) — Principal Engineer
**Date:** 2026-08-17 · **Supersedes:** `CLAUDE_TO_CODEX_PHASE_1.md` (still binding where not amended)
**Gate document:** `AUDIT_RECONCILIATION_11.md` — read it first

---

## 0. Evidentiary status of this specification — read before implementing

I could not open the audit. `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/` **do not exist** at `~/Developer/EconOS`, which is the only repo on the device matching the described tree and is a different product (a US FRED/BLS dashboard). Its `tests/` directory is empty and it contains neither `pipelines.build` nor `gei.pipeline.build`. Details and the full search in `AUDIT_RECONCILIATION_11.md` §0.

So every requirement below carries a tag:

- **[VERIFIED]** — I measured it myself against live sources this cycle or last. Implement as specified.
- **[RECONCILED]** — audit figure and my measurement explained against each other. Implement as specified.
- **[CONDITIONAL]** — a claim about repository state I cannot check. Implement **if the precondition holds**; if it does not, reply in `CODEX_TO_CLAUDE.md` and do not silently skip.

Do not upgrade a `[CONDITIONAL]` to done without stating what you found. A requirement quietly skipped because its premise was false is how the mixed-year ranking survived in the first place.

---

## 1. `[RECONCILED]` Government debt — remove `GC.DOD.TOTL.GD.ZS`

The 35-vs-15 discrepancy is **a difference of coverage definition, not a defect in either measurement**. Ever-observed = 36/50 (my measurement, IMF universe) vs latest-comparable-year = 15/50. Codex's reported latest-observation-year range of **1990–2024** reproduces exactly on my pull and is itself the proof: 17 of 50 economies have a latest debt observation before 2015 — **Germany 1990, Italy 1992, Czech Republic / Denmark / Finland / Netherlands 1994.**

**R-1.1** Remove `GC.DOD.TOTL.GD.ZS` from the metric configuration entirely. Not deprecated, not hidden behind a flag — removed, with an `excluded:` entry recording the measurement so nobody re-adds it.

**R-1.2** M-015 general government gross debt is sourced solely from **IMF WEO `GGXWDG_NGDP`**: 50/50 at 2024 and 2025, ≥45/50 from 2000. General government, not central.

**R-1.3** `OQ-11-001` — reply with the exact query producing your 35, so the 1–2 economy residual against my 36/37 is closed. Do not treat this as bookkeeping: if a filter in the metric layer is silently dropping entities, it is dropping them from every other metric too.

**R-1.4** No carry-forward is permitted to raise coverage for any metric, ever. If a 1990 observation is the newest one an economy has, that economy has no current value.

---

## 2. `[VERIFIED]` The ranking rule

This is the critical methodological defect. Specified exactly.

### R-2.1 · Every ranking is parameterised by exactly one comparison year

```
comparison_year Y is resolved BEFORE any observation values are read.

Y_default(metric) = max { y :
      coverage(metric, y) >= 0.95 * |eligible_universe|
  AND every observation at y has observation_class IN (actual, estimate)
}
```

`max(year present in the data)` is **never** the comparison year. `max(year present per entity)` is never used for ranking at all.

### R-2.2 · Ranking is computed only over entities observed at exactly Y

```
ranked   = { e in universe : obs(metric, e, Y) IS NOT NULL }
rank(e)  = dense_rank(value DESC or ASC) over `ranked`
unranked = universe \ ranked
```

- No interpolation, no last-observation-carried-forward, no nearest-year substitution. If an entity has no value at Y it is not ranked. Full stop.
- `unranked` entities are **rendered**, below the ranked rows, showing `no data at Y` and their own latest observation year. They are never silently omitted — that is P-2, and it is what makes a 15-row table look like a 50-row one.
- Ranks are never renumbered to close gaps caused by `unranked` entities; the denominator is `|ranked|` and it is displayed.

### R-2.3 · Mandatory ranking header

Every ranking view renders, non-optionally: **metric name · unit (including base year where applicable) · comparison year Y · `n ranked / |universe|` · source · source vintage.** A ranking that cannot render its comparison year does not render at all.

### R-2.4 · Multi-metric tables

In any table with several metric columns (country cards, composite leaderboards), **each column carries its own comparison year and displays it in the column header.** A single year label spanning columns with different reference years is prohibited. If the product wants one year across all columns, it must intersect: `Y_common = max{y : every displayed metric satisfies R-2.1 at y}`, and display the resulting coverage cost.

### R-2.5 · "Latest available" is a table, never a ranking

A latest-available view may exist, but it is presented as an unsorted or entity-sorted **table** with a per-row year column, and it is prohibited from carrying rank numbers or an ordered value axis. The mode is labelled `Latest available (year varies by economy)`.

---

## 3. `[VERIFIED]` Observation-year / freshness policy — designed against the USA and Argentina cases

I reproduced this finding exactly. World Bank CPI across the Top 50: metric-wide max year **2025** with **47/50**; the only two economies short are **Argentina (2024)** and **United States (2024)**; at **2024** coverage is **49/50**.

This case is the reason the R-2.1 threshold is **95% and not 90%**, and it should be read as the worked example of the whole policy:

| Candidate Y | Coverage | Under a 90% rule | Under the 95% rule |
|---|---|---|---|
| 2025 | 47/50 = **94%** | selected → **the United States is dropped from a world inflation ranking** | rejected |
| 2024 | 49/50 = **98%** | — | **selected** → US and Argentina both ranked |

A 90% threshold produces a technically-correct global inflation league table with no United States in it. That is not an edge case to handle downstream; it is a threshold chosen wrongly. **The threshold is 95%.**

### R-3.1 · Per-metric freshness fields, computed at ingest and stored

```
metric_reference_year(metric)          -- Y_default from R-2.1
metric_max_year(metric)                -- max year with ANY observation  (diagnostic only, never a comparison year)
entity_latest_year(metric, entity)
staleness_lag(metric, entity)  = metric_reference_year - entity_latest_year
```

`metric_max_year` exists to be reported, not to be used. It is the field that produced this defect.

### R-3.2 · Staleness bands and display

| Band | `staleness_lag` | Behaviour |
|---|---|---|
| current | 0 | normal render |
| lagging | 1–2 | value renders with its own year appended, e.g. `3.1% (2024)` |
| stale | 3–9 | year appended **and** a staleness marker; excluded from ranking at Y by R-2.2 |
| dormant | ≥10 | excluded from ranking; the metric is flagged for source review — Germany's 1990 debt observation is `lag = 34` |

### R-3.3 · Metric-level freshness gate

A metric whose `metric_reference_year` is more than **2 years** behind the platform reference year (D-002) is barred from the default surface and appears only in the Data Explorer with a stale-metric banner. Rationale: a "government debt" tile whose newest comparable year is 2024 is acceptable; one whose newest is 2021 is not, and the product should not decide that per-chart.

### R-3.4 · Required test cases

`TEST-F-001` uses **US CPI at 2025** — the metric must resolve `Y = 2024` and the US must be ranked. `TEST-F-002` uses **Argentina CPI at 2025** — same. `TEST-F-003` uses **German government debt** — `entity_latest_year = 1990`, band `dormant`, excluded from ranking at any modern Y, rendered as `no data at Y` with `1990` shown. These three are regression tests, not examples: they encode the two defects that reached production.

---

## 4. `[VERIFIED]` Universe: pool completeness is a separate property from year consistency

Same-year consistency across the selection and completeness of the candidate pool are independent. Verifying the first tells you nothing about the second, and the present defect is entirely in the second: World Bank `country/TWN` returns *unknown country*, and zero of 217 WB economies match "Taiwan" or "Chinese Taipei". Taiwan is ~$920bn at 2025, around rank 22. Full argument in `AUDIT_RECONCILIATION_11.md` §3.

**R-4.1** The Top-50 candidate pool is built from **IMF WEO `NGDPD`**, filtered to the IMF `/countries` reference list (D-001). The World Bank ranking is computed in parallel as a cross-check and stored, never used for selection.

**R-4.2** Selection and completeness are asserted by **two independent tests that cannot substitute for each other**:

- `TEST-U-006` **pool completeness** — candidate pool size ≥ 190 **and** contains `TWN` **and** contains every entity whose eligibility is `include` (§5). Fails independently of any year logic.
- `TEST-U-007` **selection year consistency** — every value used to rank the pool comes from the same year, and that year equals the resolved `ref_year`. Fails independently of pool contents.

Both must pass. Neither passing is evidence about the other. Wire them as separate test functions with separate failure messages, so a green `TEST-U-007` can never be read as coverage assurance.

**R-4.3** The universe artefact records `pool_source`, `pool_size`, `ref_year`, `n_ranked`, and `excluded_ineligible`, so the frame is inspectable without re-running the build.

---

## 5. `[VERIFIED at source]` Analytical-entity eligibility — an explicit field, not an inference

**Root cause, confirmed at the source rather than assumed:** the World Bank `/country` object exposes exactly `id, iso2Code, name, region, adminregion, incomeLevel, lendingType, capitalCity, latitude, longitude`. **There is no sovereignty, statehood, or territory field.** Hong Kong returns `adminregion: ""`. So a null territory classification for every economy is the *correct* output of any pipeline over these sources — the defect is that a field requiring information the sources do not carry was modelled as inferable at all.

**Do not attempt to infer sovereignty, statehood, or territorial status programmatically, and do not invent geopolitical classifications.** Name matching, region heuristics, and `adminregion` emptiness are all prohibited as eligibility signals.

**R-5.1** Replace the inferred territory field with an explicit, version-controlled reference table `config/entities.yaml`, keyed by ISO 3166-1 alpha-3:

```yaml
- iso3: HKG
  iso2: HK
  un_m49: 344                      # authoritative identifier, not a judgement
  name_imf: "Hong Kong SAR"
  name_wb:  "Hong Kong SAR, China"
  source_membership: {imf_weo: true, wb_wdi: true}
  reporting_entity: true           # compiles its own national accounts
  consolidated_into: null          # double-count guard; iso3 if its accounts sit inside another's
  eligibility: include
  eligibility_reason: "Separate national accounts; not consolidated into CHN."
  decided_by: claude
  decided_on: 2026-08-17
```

`eligibility ∈ {include, exclude_aggregate, exclude_consolidated, review}`.

**R-5.2** **The default for any entity code newly appearing in a source is `review`, and the build FAILS if any `review` entity reaches the universe.** This is the load-bearing rule. It converts "a new code appeared and we guessed" into "a human decided," and it is the only mechanism that prevents this class of defect recurring when a source adds an entity.

**R-5.3** Codex implements the schema, the loader, the gate, and the failing test. **Codex does not populate `eligibility` or `eligibility_reason`** — those values are supplied by me and the owner (`OQ-11-004`). Seed the file mechanically from `IMF /countries ∪ WB region.id != "NA"` with every row at `eligibility: review`, and hand it back for adjudication.

**R-5.4** `TEST-E-001` — no entity with `eligibility: review` appears in the universe. `TEST-E-002` — no entity with a non-null `consolidated_into` appears alongside its parent (double-count guard). `TEST-E-003` — eligibility is never derived from `name`, `region`, or `adminregion`; assert by fixture that an entity with empty `region` and empty `adminregion` still resolves correctly from the explicit table.

---

## 6. `[CONDITIONAL]` Tests must target the production universe path

**Precondition I could not check:** `tests/test_universe.py` importing `pipelines.build` while production uses `gei.pipeline.build`. At the cited repo `tests/` is empty and neither module exists. If the precondition is false, say so in `CODEX_TO_CLAUDE.md` rather than implementing around it.

**Classification: a testing problem of severity high — false assurance.** Record it that way in the audit, not as "a test needing an update." A test exercising a module the application does not import **cannot fail when production breaks**, and it emits a green signal that actively suppresses investigation. It should be counted as a missing test *plus* a misleading signal. On the evidence, it is a plausible proximate reason the mixed-year ranking and the incomplete pool both survived to release.

**R-6.1** Every Phase 1.1 test imports the production entrypoint **by the identical module path the application resolves**. No test may import a universe-building module that production does not import.

**R-6.2** Add `TEST-T-001`, an import-provenance guard: assert that the module object exercised by the universe tests is the same object the application resolves — compare `__file__`/module identity against the application's import, so a future divergence fails loudly instead of drifting.

**R-6.3** Add a repo-level check that fails CI if any test imports a module path with no production importer. This catches the general class, not this instance.

**R-6.4** **Delete `pipelines.build` if it is legacy** (`OQ-11-003`). The root cause is not the test pointing at the wrong module; it is that two universe-build paths coexist and one shadows the other. Testing the correct one while leaving the other in the tree leaves the trap armed. If anything in production still imports it, that is a larger finding than the test and needs to come back to me.

**R-6.5** Port `TEST-U-001` … `TEST-U-007`, `TEST-F-001` … `TEST-F-003`, `TEST-E-001` … `TEST-E-003` onto the production path. Any Phase-1 test currently passing against a non-production module counts as **not implemented**.

---

## 7. `[VERIFIED]` Define coverage before reporting it

The 35-vs-15 discrepancy consumed this cycle because "coverage" was unqualified. It is now a typed quantity, and no coverage figure may be emitted without its type.

```
coverage_ever(metric)          -- entities with >=1 observation in any year
coverage_at(metric, Y)         -- entities with an observation at exactly Y
coverage_recent(metric, Y, k)  -- entities with an observation in [Y-k, Y]
```

**R-7.1** Every coverage figure in logs, audits, tests, the Data Explorer, and the methodology page is emitted with its type and its year. A bare "35/50" is prohibited output.

**R-7.2** `coverage_at(metric, metric_reference_year)` is the **only** coverage type permitted to gate a metric's inclusion on a ranking surface. `coverage_ever` is diagnostic and may never gate anything — on the debt metric it overstates usable coverage by 21 economies.

**R-7.3** The Data Explorer displays all three per metric, side by side. The gap between them is the product's most honest single indicator of data quality.

---

## 8. Blocking tests added in Phase 1.1

| ID | Assertion | Basis |
|---|---|---|
| `TEST-U-006` | Candidate pool ≥190 entities, contains `TWN`, contains every `eligibility: include` entity | [VERIFIED] |
| `TEST-U-007` | All selection values share one year, equal to the resolved `ref_year` | [VERIFIED] |
| `TEST-R-001` | No ranking is produced without a resolved `comparison_year` | [VERIFIED] |
| `TEST-R-002` | No ranked row's observation year differs from the ranking's `comparison_year` | [VERIFIED] |
| `TEST-R-003` | Entities lacking an observation at Y appear as `no data at Y` rows and are not omitted | [VERIFIED] |
| `TEST-R-004` | Multi-metric tables render a per-column comparison year | [VERIFIED] |
| `TEST-F-001` | US CPI: metric resolves Y = 2024; the US is ranked | [VERIFIED] |
| `TEST-F-002` | Argentina CPI: metric resolves Y = 2024; Argentina is ranked | [VERIFIED] |
| `TEST-F-003` | German govt debt: `entity_latest_year` = 1990, band `dormant`, excluded from ranking, year rendered | [VERIFIED] |
| `TEST-E-001` | No `eligibility: review` entity reaches the universe (build fails) | [VERIFIED at source] |
| `TEST-E-002` | No entity appears alongside its `consolidated_into` parent | [VERIFIED at source] |
| `TEST-E-003` | Eligibility resolves from the explicit table for an entity with empty `region` and `adminregion` | [VERIFIED at source] |
| `TEST-C-001` | No coverage figure is emitted without a type and year | [VERIFIED] |
| `TEST-T-001` | Universe tests exercise the same module object the application resolves | [CONDITIONAL] |
| `TEST-T-002` | CI fails if any test imports a module with no production importer | [CONDITIONAL] |

All Phase-1 blocking tests (`CLAUDE_TO_CODEX_PHASE_1.md` Part 3) remain in force.

---

## 9. Sequencing

1. **R-1** remove the debt metric, switch to `GGXWDG_NGDP`, answer `OQ-11-001`.
2. **R-6.4** resolve the duplicate build path (`OQ-11-003`) — do this before writing tests, or the tests get written against the wrong module again.
3. **R-2** implement the ranking rule and `TEST-R-001…004`. Highest severity: it is publishing wrong orderings now.
4. **R-3** freshness fields and `TEST-F-001…003`.
5. **R-4** pool source and the two independent universe tests.
6. **R-5** seed `config/entities.yaml` at `review` and hand back for adjudication; implement the gate.
7. **R-7** coverage typing.

## 10. Reply required in `CODEX_TO_CLAUDE.md`

1. `OQ-11-001` — the query yielding 35 ever-observed.
2. `OQ-11-002` — the real location of `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/`. Findings #5 and #6 stay unverified until then, and §6 stays `[CONDITIONAL]`.
3. `OQ-11-003` — is `pipelines.build` legacy and deletable?
4. Confirmation for each `[CONDITIONAL]` requirement: precondition held, or did not hold and why.
5. The seeded `config/entities.yaml` with every row at `eligibility: review`, for adjudication.
