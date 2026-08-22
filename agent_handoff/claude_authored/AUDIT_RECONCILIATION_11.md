# Audit reconciliation — Phase 1.1 gate
**Agent A (Claude)** · 2026-08-17 · **Status: one blocking evidence gap, one finding fully reconciled**

---

## 0. Blocking notice — the cited audit artefacts do not exist

I was asked to incorporate evidence at `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/`. **Neither path exists.** I searched the device rather than assuming:

| Checked | Result |
|---|---|
| `~/Developer/EconOS/docs/audit/` | **does not exist**. `docs/` holds 11 markdown files + `screenshots/`; no audit directory |
| `~/Developer/EconOS/data/audit/` | **does not exist**. `data/` holds `metadata/series_registry.json` + `processed/*.json` |
| `~/Developer/EconOS/tests/` | **empty — zero files.** `tests/test_universe.py` does not exist |
| `~/Developer/EconOS/pipelines/` | only `ingest/fetch_fred.py`, `validate/validate_processed.py`. No `pipelines/build.py`, no `gei/` package. **Neither `pipelines.build` nor `gei.pipeline.build` exists** |
| Repo contents | US macro series — `cpi_all`, `payrolls`, `mortgage_30y`, `treasury_10y`, `case_shiller_national`, `yield_spread_10y2y`. **No country panel, no Top-50 universe, no government-debt metric** |
| Other repos on device | `Projects/lantern-ny`, `dev/jls-*`, `Developer/debtscope-ai`, `Developer/alaso`, `PycharmProjects/*`, `build`, `test2`, `jeanlucs` — none is a Top-50 country-panel project |

`~/Developer/EconOS` is the only repo whose tree matches the description (`docs/`, `data/`, `pipelines/`, `tests/`), and it is a **different product**: a US macroeconomic dashboard built on FRED/BLS series.

**Consequence:** I cannot read Codex's audit, so I cannot confirm any of the six findings *as measurements Codex made*. What I can do — and did — is test each finding independently against the live sources. Four of six reproduce exactly or near-exactly on my own evidence and are specified below as confirmed. Two are claims about repository state that I have no way to verify and that are contradicted by what is actually on disk at the cited location.

Every requirement in the Phase 1.1 spec is tagged with its evidentiary basis. Nothing is written as confirmed on the strength of an audit I could not open.

---

## 1. Reconciling 35/50 against 15/50 — **resolved: different coverage definitions**

This was the explicit blocker, and it is now closed with measurement rather than argument.

I re-pulled World Bank `GC.DOD.TOTL.GD.ZS` for the full history (1960–2026) and counted it two different ways against both candidate universes:

| Counting method | IMF Top-50 | WB Top-50 |
|---|---|---|
| **Ever observed** (any year in history) | **36 / 50** | **37 / 50** |
| Observed at 2020 | 18 / 50 | 18 / 50 |
| Observed at 2022 | 17 / 50 | 17 / 50 |
| Observed at 2023 | 16 / 50 | 16 / 50 |
| **Observed at 2024** (latest year with any data) | **15 / 50** | **15 / 50** |
| Observed at 2025 | 0 / 50 | 0 / 50 |
| **Range of per-entity latest observation years** | **1990 – 2024** | **1990 – 2024** |

**The two figures measure different quantities and both are correct.**

- Codex's **35/50 with 15 having none** is an *ever-observed* count: has this entity ever had a debt observation, at any point in history?
- My **15/50** is a *latest-comparable-year* count: does this entity have an observation at the most recent year where a cross-country comparison is possible?

The decisive corroboration is the year range. Codex reported latest observation years spanning **1990–2024**, and I measure **exactly 1990–2024** independently. That range is only producible by an ever-observed count — and it is itself the proof of the problem:

| Economy | Latest `GC.DOD.TOTL.GD.ZS` observation |
|---|---|
| Germany | **1990** |
| Italy | **1992** |
| Czech Republic | 1994 |
| Denmark | 1994 |
| Finland | 1994 |
| Netherlands | 1994 |

**17 of the 50 have a latest debt observation before 2015.** So the ever-observed count of ~35 is not evidence that the metric is two-thirds usable. It is evidence that the metric *was* populated for many economies decades ago and has since been discontinued for most of them. Presenting it as coverage is the same category error as presenting Germany's 1990 debt ratio next to Brazil's 2024 one — which is precisely finding #2.

**Cause classification: different coverage definitions.** Not a different universe (the two universes give 36 vs 37 — a one-economy difference, immaterial to the discrepancy), not pipeline behaviour, not metric configuration.

**Residual to close (1–2 economies).** Codex reports 35 ever-observed; I measure 36 against the IMF universe and 37 against the World Bank universe. The residual is small but unexplained, and the instruction not to proceed on an unexplained discrepancy applies to the residual too. Candidate causes, in order of likelihood: (a) the implemented metric applies a filter I am not applying — e.g. a minimum-observations threshold, a year floor, or dropping single-observation series; (b) the implementation's universe differs from both of mine by one member; (c) a null-vs-zero handling difference. **`OQ-11-001` — Codex to state which, with the query that produces 35.** This does not block the Phase 1.1 spec, because the disposition (drop `GC.DOD.TOTL.GD.ZS`, use IMF WEO `GGXWDG_NGDP`, 50/50 at both 2024 and 2025) is unchanged under any of the three.

**Disposition is unaffected and firm:** whether the number is 15, 35, or 37, the metric is unusable for cross-country comparison. Fifteen economies at the latest year, and a median latest-observation year well before the reference year, fails on both axes. Phase 1.1 removes it.

---

## 2. Independent status of each finding

| # | Finding as stated | My independent evidence | Status |
|---|---|---|---|
| 1 | Debt metric: 35/50 observed, 15 none, latest years 1990–2024 | Ever-observed **36/50**; latest-year **15/50**; range **1990–2024** exactly | **Reconciled** — definitional. Residual 1–2 economies → `OQ-11-001` |
| 2 | Rankings can compare observations from different years | Independently established last cycle (G-13, D-002); the 1990–2024 debt range above is a live instance | **Confirmed** |
| 3 | USA and Argentina inflation end 2024; metric-wide max is 2025 | Re-measured: WB CPI metric-wide max **2025**, **47/50** at 2025; the only two economies short are **Argentina (2024)** and **United States (2024)**; **49/50** at 2024 | **Confirmed — exact reproduction** |
| 4 | All Top-50 GDP selections use common year 2025 | Not verifiable (no repo). Independently: WB nominal GDP at 2025 covers 186 economies and **contains no Taiwan at any year** | **Half-confirmed** — see §3 |
| 5 | `tests/test_universe.py` tests `pipelines.build`, not `gei.pipeline.build` | `tests/` at the cited repo is **empty**; neither module exists anywhere in it | **Unverifiable** — specified conditionally |
| 6 | Territory classification null for every selected economy | Not verifiable. But confirmed at source: WB `/country` exposes only `id, iso2Code, name, region, adminregion, incomeLevel, lendingType, capitalCity, latitude, longitude`. **No sovereignty or territory field exists.** Hong Kong returns `adminregion: ""` | **Root cause confirmed at source** — null is the expected output, not a bug |

---

## 3. Finding #4 — same-year consistency is not universe completeness

These are two independent properties and the audit result on one says nothing about the other.

**P1 — temporal consistency of the selection.** Do all values used to rank the candidate pool come from one year? Reported: yes, 2025. This is a property of *the comparison*.

**P2 — completeness of the candidate pool.** Does the pool contain every economy that ought to be eligible? **No.** World Bank has no Taiwan — not a null, not a gap: `country/TWN` returns *unknown country*, and zero of 217 WB economies match "Taiwan" or "Chinese Taipei". This is a property of *the frame*.

P1 can hold perfectly while P2 fails completely, and that is exactly the present state. A selection can be flawlessly year-consistent across the wrong set of candidates. Verifying P1 produces a green signal that is true and irrelevant to the defect.

Concretely: at 2025 Taiwan is ~$920bn (IMF WEO), around rank 22. Every Top-50 built from the World Bank pool omits it and pulls one extra economy up from below the line. Making all selection values share the year 2025 does not move Taiwan into the pool, because Taiwan is not in the pool at any year.

**The fix is the candidate source, not the year logic.** Phase 1.1 ranks on IMF WEO `NGDPD`, and adds a pool-completeness test that is independent of the year-consistency test (`TEST-U-006`, `TEST-U-007` below). Both must pass; neither substitutes for the other.

---

## 4. Problem classification

### SOURCE PROBLEMS
*Defects in the upstream data. No code change fixes these; only source substitution or explicit disclosure.*

- **S-1 · World Bank `GC.DOD.TOTL.GD.ZS` is discontinued for most economies.** 15/50 at the latest year; 17/50 have a latest observation before 2015; Germany's is **1990**. Also *central* government, not general. → replace with IMF WEO `GGXWDG_NGDP` (50/50, 2024 and 2025).
- **S-2 · World Bank contains no Taiwan.** Not missing data — the entity does not exist in the source. Caps every WB-sourced metric at 49/50 and makes a WB-based Top-50 structurally incomplete.
- **S-3 · World Bank CPI publication lags for the US and Argentina.** Metric-wide max 2025 (47/50); US and Argentina latest 2024.
- **S-4 · No source exposes a sovereignty or territory field.** WB `/country` returns ten fields, none of them sovereignty; Hong Kong's `adminregion` is empty. Territory classification cannot be derived from the sources at all.
- **S-5 · IMF DataMapper returns projections to 2031 unflagged** (carried from Phase 1, unresolved).

### METHODOLOGY PROBLEMS
*The system computes something well-defined that does not mean what it appears to mean.*

- **M-1 · Rankings compare observations from different years.** With debt, this places Germany-1990 beside Brazil-2024 in one sorted column. Severity: **critical** — it produces confidently wrong orderings, not visible gaps.
- **M-2 · "Coverage" is undefined at the product level.** Ever-observed and latest-year-observed differ by 21 economies on a single metric (36 vs 15). Any coverage statement without a stated definition is unfalsifiable — this is the entire content of the 35-vs-15 discrepancy.
- **M-3 · Universe completeness and selection-year consistency were conflated.** §3.
- **M-4 · "Latest available year" as a default is not a methodology.** It selects a different year per entity and calls the result a comparison.

### IMPLEMENTATION PROBLEMS
*Code does not do what the spec requires. **All unverifiable — the cited repo does not contain this pipeline.***

- **I-1 · Territory/eligibility field is null for every economy.** Expected given S-4. The defect is not the null; it is that a nullable inferred field was modelled at all where no source field exists.
- **I-2 · Two universe-build paths appear to coexist** (`pipelines.build`, `gei.pipeline.build`). A legacy module shadowing the production one is the root cause of the testing problem below, and should be deleted rather than tested.
- **I-3 · Ranking layer permits mixed-year comparison** — the code-side expression of M-1.

### TESTING PROBLEMS

- **T-1 · The universe test targets a non-production module.** Classification: **false assurance, severity high.** This is worse than having no test. A test that exercises a module the application does not import cannot fail when production breaks, and it emits a green signal that suppresses the investigation that would have found M-1 and M-3. It should be counted as a *missing* test plus an *actively misleading* signal, not as a test needing an update. **Unverifiable at the cited repo — `tests/` is empty.**
- **T-2 · No test pins the comparison year.** M-1 survived, so no assertion covers it.
- **T-3 · No test asserts pool completeness independently of year consistency.** M-3 survived for the same reason.

### PRODUCT / UX PROBLEMS

- **P-1 · Rankings display no comparison year**, so a mixed-year ordering is indistinguishable from a valid one to the user. This is what converts M-1 from an internal defect into a published false claim.
- **P-2 · Absent entities vanish rather than appearing as "no data."** A 15-row debt league table labelled "Top 50" misrepresents its own coverage.
- **P-3 · Taiwan's absence is invisible.** No user can tell the pool was incomplete.
- **P-4 · No staleness indication.** Germany's 1990 debt figure renders identically to Brazil's 2024 one.

---

## 5. Open questions raised by this cycle

| ID | Question | Owner |
|---|---|---|
| **OQ-11-001** | Codex reports 35 ever-observed; I measure 36 (IMF universe) / 37 (WB universe). Which filter accounts for the residual? Provide the query that yields 35. | Codex |
| **OQ-11-002** | Where do `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/` actually live? They are not at `~/Developer/EconOS`, which is a different product. Until located, findings #5 and #6 remain unverified. | Owner / Codex |
| **OQ-11-003** | Is `pipelines.build` legacy and deletable? If it is still imported by anything in production, that is a larger problem than the test. | Codex |
| **OQ-11-004** | Eligibility values for the ~200-economy pool require a human decision per entity (§6 of the spec). Confirm the owner supplies these rather than Codex inferring them. | Owner |
