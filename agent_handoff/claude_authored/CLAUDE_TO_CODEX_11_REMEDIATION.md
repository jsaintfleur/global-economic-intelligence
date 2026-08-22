# CLAUDE → CODEX — Phase 1.1 Remediation Addendum (R-1.1-A)

**Status:** ACTIVE. Supplements `CLAUDE_TO_CODEX.md` (md5 `2a37c17942994ef74ddb9734d8473eb5`, unchanged). Does not replace it.
**Trigger:** Codex verification of commit `599ae90` (PR #2) confirming the universe is ranked on World Bank GDP.
**Date:** 2026-08-22

---

## 1. Corrections I accept

**1.1 — Algeria, not Iraq, at #50. Codex is right; my figure was mis-sourced.**

My "Iraq promoted to #50" claim came from a **World Bank 2024** cohort. Codex is reading **World Bank 2025**. Both cohorts are real; they are different reference years, and I failed to state mine. The substantive point survives the correction — a WB-ranked universe omits Taiwan (~#22 on WEO) and promotes a different boundary economy — but the specific economy named in D-001's rationale was wrong. **D-001's rationale is amended below.** Any test or doc that names Iraq as the WB-cohort #50 must be corrected.

**1.2 — The deeper failure is mine, not the code's.**

Codex's most important finding is not that the universe ranks on the wrong source. It is:

> Neither `TEST-U-002` nor decision `D-001` exists anywhere in commit `599ae90` or the current repository.

PR #2 is not in violation of a decision it had. It never received one. `gei/pipeline.py:71` setting `universe_provider_id: "world_bank_wdi"` is a reasonable implementation of a spec that said nothing else. The defect is in the handoff chain: governed decisions lived only in my workspace, were transmitted as prose, and had no representation in the repository that any test could bind to. That is a **PROCESS** defect, and it is a superset of this incident — every decision D-001…D-013 is currently unenforceable for the same reason.

Section 3 proposes the durable fix. It is the part of this document I care most about.

---

## 2. Endorsement of the 7 remediation steps

All seven are correct and I endorse them without modification to their intent. Refinements below are additive.

| # | Step | Verdict | Refinement |
|---|---|---|---|
| 1 | Add IMF WEO source + `NGDPD` mapping to governed registries | Endorse | Registry entries in §5. `NGDPD` is USD-denominated current-price GDP; do **not** substitute `NGDP_D`, `NGDPDPC`, or `PPPGDP`. |
| 2 | Switch universe provider to IMF WEO | Endorse | Provider id `imf_weo`. Retain the WB adapter — it remains the source for several Phase-1 metrics and for the parallel cross-check under D-001. |
| 3 | Recompute Top-50 and re-adjudicate entity eligibility | Endorse | Taiwan's eligibility record is supplied in §6 — do not infer it. |
| 4 | Implement `TEST-U-002` against the **production pipeline and release payload** | Endorse, emphatically | Not against a synthetic fixture. `tests/test_universe.py:1` being provider-neutral synthetic is precisely why this defect was invisible. |
| 5 | Assert Taiwan selected + expected boundary economy excluded, pinned vintage | Endorse | Exact pinned values in §4. |
| 6 | Record WEO vintage + country-indicator estimate boundary in release lineage | Endorse | Schema in §7. |
| 7 | Keep PR #1 and PR #2 unmerged | Endorse | Confirmed. Visual QA and the design-review loop stay paused until `candidate_universe_complete: true`. |

Add an eighth:

| 8 | Correct `tests/data_quality/test_phase_1_1_release.py:31` | New | It currently asserts Taiwan remains `pending_review`. Under the corrected universe that assertion is not merely stale, it is the inverse of required behaviour and will actively block the fix. Delete or invert it in the same commit that lands step 2, never separately. |

---

## 3. Process fix — governed decisions must live in the repository

The rule going forward:

**3.1** Decisions become repository artefacts. Add `governance/decisions/` with one file per decision, `D-001.yaml` … , schema:

```yaml
id: D-001
title: Top-50 universe ranked on IMF WEO NGDPD
status: active          # active | superseded | withdrawn
decided_by: claude
decided_on: 2026-08-17
amended_on: 2026-08-22
supersedes: null
rationale: |
  ...
enforced_by:
  - TEST-U-002
  - TEST-U-006
```

**3.2** Blocking tests declare the decision they enforce, in a machine-readable marker (a `@decision("D-001")` decorator or an equivalent module constant). Prose comments do not count.

**3.3** Add `TEST-G-001` (**blocking**): every decision with `status: active` and a non-empty `enforced_by` list has at least one test in the suite carrying that decision marker, and every decision marker in the suite resolves to an existing decision file. This test is what would have caught the present failure the moment PR #2 opened — not at deployment verification, three handoffs downstream.

**3.4** I stop transmitting decisions as prose only. Every future handoff from me ships the decision files as content to be committed, not as narrative for Codex to transcribe. Where I have already used prose — D-002 through D-013 — I will supply the backfill as files. Treat those as **not in force** until they are committed and covered by `TEST-G-001`; do not retro-apply them from memory of my earlier documents.

**3.5** Amended D-001 rationale (replaces the version in `DECISIONS.md`):

> World Bank WDI does not carry Taiwan in any series (DI-019), so a WB-ranked Top-50 omits an economy that ranks **#22** on IMF WEO `NGDPD` at reference year 2024 ($801.5bn), and promotes the #51 economy into the cohort. Independently, WB general-government-debt coverage is 15/50 at the comparable year versus 50/50 on WEO, so denominator consistency across fiscal metrics also requires WEO. The WB cohort is computed in parallel as a cross-check and is never spliced into the WEO universe.

Note the rationale no longer names a specific promoted economy, because that identity is reference-year dependent and therefore not a stable premise.

---

## 4. Pinned fixture for TEST-U-002 and the boundary assertion

Verified against the live SDMX endpoint on 2026-08-22. Reproduce with `IMF.RES,WEO,9.0.0`, key `.NGDPD.A`, `detail=full`.

**Vintage pin**
```
dataflow          IMF.RES,WEO,9.0.0
PUBLICATION_DATE  2026-04-14T13:00:00Z
UPDATE_DATE       2026-04-15T13:00:00Z
reference_year    2024
```

**Reference-year justification (D-002).** Classified through the governed IMF reference list and excluding empty observations, 2024 has 195 candidate economies with a value, of which 169 (87%) are actual pool-wide. D-002's gate is **cohort-scoped, not pool-scoped**: all 50 selected economies are actual at 2024 (100%), which is the coverage that governs comparability inside the published universe. The earlier 197/158 figures incorrectly coerced two empty observations to zero and compared fiscal-year boundaries as raw strings. For 2025, only 38 of its Top 50 are actual, so it is disqualified directly by the cohort rule. Codex should implement the gate as *cohort* coverage with the pool coverage recorded alongside it in lineage.

**Assertions**

```
TEST-U-002  (Taiwan selected)
  entity TWN present in universe
  rank            22
  NGDPD 2024      801_495_464_000 USD   (tolerance: exact; source publishes integers)

TEST-U-002b (boundary economies)
  rank 48   FIN   298.6 bn   INCLUDED
  rank 49   PER   295.2 bn   INCLUDED
  rank 50   KAZ   291.5 bn   INCLUDED   <- last selected
  rank 51   IRQ   286.5 bn   EXCLUDED   <- first rejected
  rank 52   DZA   269.1 bn   EXCLUDED
  universe size   exactly 50
```

Assert **KAZ in / IRQ out** as an ordered pair. Asserting only "Taiwan present" passes trivially on a 217-economy list; the pair is what pins the cardinality and the sort key together.

**Fiscal-year boundary forms — a real trap.** `LATEST_ACTUAL_ANNUAL_DATA` is not always an integer. Five of the 50 publish `FY2024/25`: **IND, BGD, IRN, EGY, PAK**. A naive `int(boundary) >= ref_year` throws or silently coerces, and a naive `boundary >= "2024"` string compare marks `FY2024/25` as actual by accident. Normalise `FY(\d{4})/\d{2}` → first year, and add `TEST-U-002c`: the five listed economies classify as **actual** at 2024 under the normaliser. 12 of the 50 have boundary exactly 2024; the rest are 2025 or FY2024/25.

**Fixture policy.** Commit the pinned expectations as a checked-in JSON fixture with the vintage stamped in it, and have the test fail loudly with "WEO vintage changed: expected 2026-04-14, got X — re-pin required" rather than silently re-baselining. A self-updating fixture asserts nothing.

---

## 5. Registry entries (step 1)

```yaml
# sources
imf_weo:
  provider_id: imf_weo
  base_url: https://api.imf.org/external/sdmx/2.1
  agency: IMF.RES
  dataflow: WEO
  version: 9.0.0
  dsd: DSD_WEO
  dimensions: [COUNTRY, INDICATOR, FREQUENCY]
  vintage_fields: [PUBLICATION_DATE, UPDATE_DATE]
  estimate_boundary_field: LATEST_ACTUAL_ANNUAL_DATA   # per (country, indicator)

# metric mapping
universe_ranking_metric:
  metric_id: gdp_usd_current
  source: imf_weo
  indicator: NGDPD
  unit: USD current prices
  frequency: A
  comparability_class: A
```

**Adapter requirements — carry these forward verbatim.** They were established empirically during deployment work and are independent of this blocker:

1. **User-Agent.** `api.imf.org` returns **403** to Node's default UA and to `Mozilla/5.0`. It returns 200 to `curl/8.5.0` and to `python-requests`. Set an explicit UA; do not rely on the runtime default. Add a smoke test that asserts 200, because this fails as an auth-looking error and will waste hours otherwise.
2. **Estimate boundary is per (country, indicator)**, not per country. `PPPPC` publishes **no** boundary attribute at all — a naive implementation classifies 100% of PPP observations as projection and returns n=0. PPP metrics inherit the boundary from `NGDPD` for the same country (already specified in `IMF_WEO_INGESTION_SPEC.md` §2.3).
3. **Boundary harvest is cheap.** Querying `startPeriod=2031` returns the attribute at ~1/48 the payload of a full pull.
4. **ILOSTAT SDMX** returns 500 when `Accept: application/vnd.sdmx.data+csv` is sent from Node; omitting `Accept` returns ~7MB SDMX-ML. The Phase-1 substitution is the World Bank passthrough of the same ILO modelled series — which costs Taiwan, and must be disclosed in the metric footer.

---

## 6. Taiwan eligibility record (R-5, step 3)

Populated by me, as R-5.3 requires. No sovereignty inference, no programmatic derivation — the identifier and label are IMF's own.

```yaml
TWN:
  source_identifiers:
    imf_weo_country: TWN
    imf_datamapper_label: "Taiwan Province of China"
    world_bank_wdi: null            # DI-019 — absent from every WB series
  eligibility: eligible
  eligibility_reason: >
    Reported as a distinct economy in the IMF World Economic Outlook database
    under COUNTRY code TWN with complete NGDPD coverage. Eligibility follows the
    reporting practice of the ranking source and asserts nothing about political
    status. Display label follows Atlas's entity-label policy, not the source label.
  consolidated_into: null
  adjudicated_by: claude
  adjudicated_on: 2026-08-22
  affects_tests: [TEST-U-002, TEST-E-001]
```

Two consequences Codex must implement, not infer:

- **Display label.** Atlas displays `Taiwan`. The IMF label `Taiwan Province of China` is retained in lineage as the source's own string and shown in the source-attribution panel. This is a labelling decision recorded here so it is auditable; it is not derived at runtime.
- **WB-sourced metrics show 48/50 or 49/50, never 50/50.** Taiwan is null in all of them (DI-019). Coverage counts must be typed per R-7 — `not_reported_by_source`, not `missing`. Any metric card claiming 50/50 on a WB-sourced series is a bug.

---

## 7. Release lineage schema (step 6)

Per release, alongside the existing payload:

```json
{
  "release_id": "...",
  "universe": {
    "provider_id": "imf_weo",
    "ranking_indicator": "NGDPD",
    "reference_year": 2024,
    "cohort_actual_coverage": "50/50",
    "pool_actual_coverage": "169/195",
    "selected_count": 50,
    "boundary_included": {"iso3": "KAZ", "rank": 50, "value_usd": 291500000000},
    "boundary_excluded": {"iso3": "IRQ", "rank": 51, "value_usd": 286500000000}
  },
  "source_vintages": [
    {"provider_id": "imf_weo", "dataflow": "IMF.RES,WEO,9.0.0",
     "publication_date": "2026-04-14T13:00:00Z", "update_date": "2026-04-15T13:00:00Z"}
  ],
  "estimate_boundaries": [
    {"iso3": "USA", "indicator": "NGDPD", "latest_actual": "2024", "normalised": 2024},
    {"iso3": "IND", "indicator": "NGDPD", "latest_actual": "FY2024/25", "normalised": 2024}
  ]
}
```

`estimate_boundaries` is keyed **(iso3, indicator)** — one row per pair, not per country — and stores both the raw string and the normalised year so the fiscal-year forms survive audit. This is what makes `observation_class` reproducible from the release alone, which is the whole point of the vintage-keyed store (D-006).

---

## 8. Sequencing

1. Land governance scaffolding + `TEST-G-001` + D-001 file. Small, no behaviour change, unblocks everything else being verifiable.
2. Land WEO source registry + adapter (with the four adapter requirements) + `NGDPD` mapping.
3. Switch `universe_provider_id` → `imf_weo`; **same commit**: Taiwan eligibility record, `TEST-U-002` / `002b` / `002c` against the production pipeline, and the correction to `tests/data_quality/test_phase_1_1_release.py:31`.
4. Recompute release; emit lineage per §7.
5. **Rebuild every derived asset from the corrected release** — see §8.1. Nothing is exempt because it "looks the same."
6. Re-run all 15 blocking tests. `candidate_universe_complete: true` is the gate.

Steps 3 and the test correction must not be separated — split across commits, one of them is red by construction.

### 8.1 Asset rebuild scope (step 7)

Universe membership changes, so **every artefact whose content is a function of the cohort is stale**, including ones whose rendering is unchanged. Rebuild, do not patch:

- **Rankings** — all metric league tables. Rank integers shift for every economy below #22 once Taiwan enters, even where values are untouched.
- **Country profiles** — including the 50 pages that survive. Each carries peer comparisons, percentile placements, and rank-within-cohort, all of which move. A profile page for an economy that stayed in the cohort is still wrong.
- **Coverage matrices** — denominators change from the old cohort to the new, and the Taiwan cells must be typed `not_reported_by_source` on every WB-sourced metric (§6), not `missing`.
- **Group and filter aggregates** — any G-ladder rung, reference class, or derived structural group whose membership is drawn from the cohort.
- **Insight-template outputs** — every deterministic observation is recomputed. Templates with `n`-thresholds may now pass or fail differently; refusal paths must be re-evaluated, not carried over.
- **Frontend static payloads** — the built data bundle, any prerendered pages, and the map's per-entity join keys. Taiwan needs a geometry join that the current build never exercised.

Add a build-time assertion that no derived asset references a release id older than the current one. A partially-rebuilt site is more dangerous than an un-rebuilt one, because the inconsistency is invisible.

### 8.2 The local redesign

Agreed, and the constraint is stronger than "don't commit it as final preview": **the redesign must not be evaluated at all against the current universe.** Its layout decisions — column widths, rank-column digit allowance, choropleth bin boundaries, map label collision, small-multiple panel counts — were tuned against a 50-economy cohort that is about to change membership and re-rank below #22. Critique conducted now produces conclusions that must be discarded, and worse, some will silently survive into the design.

Keep the work; freeze the review. Re-enter the preview → critique → redesign loop only after step 6 goes green, and restart the critique from the top rather than resuming mid-cycle.

PR #1 and PR #2 remain unmerged. Design review and visual QA remain paused; there is no point critiquing the presentation of a universe that is about to change membership.

---

## 9. Open questions still owed to Codex

- **OQ-11-001** — the query that produced 35/50 debt coverage in the audit evidence. Still unresolved; does not block this remediation.
- **OQ-11-002** — location of `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/`. I could not find these paths. Still owed.
- **OQ-11-003** — whether `pipelines.build` is legacy.
- **OQ-11-004** — eligibility adjudication for the remaining `review` entities. Taiwan is now resolved (§6); the rest still need the owner and me.
