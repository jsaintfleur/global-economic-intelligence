# Claude → Codex: Phase 1.1 Implementation Specification

## Status and authority

This specification incorporates the audit bundle for `release_e9182edbdb3e275e19ca`. It authorizes Phase 1.1 implementation only. Do not begin Phase 2, add forecasting, scoring, ML, or silently substitute economic sources or definitions.

Primary evidence:

- `docs/audit/README.md`
- `docs/audit/PHASE_1_1_FINDINGS.md`
- `data/audit/release_e9182edbdb3e275e19ca/`

## Decisions by problem class

### SOURCE PROBLEMS

1. **Debt scope and coverage must remain explicit.** The current indicator is World Bank WDI `GC.DOD.TOTL.GD.ZS`, labelled “Central government debt, total (% of GDP),” with underlying source metadata identifying IMF Government Finance Statistics. Do not describe it as general-government gross debt.
2. **Reconciled coverage:** 35/50 means at least one accepted observation during 1990–2025; 15/50 means an observation in 2024, the metric-wide latest year. These are the same metric, same Top-50 universe, identity transformation, and release. The difference is historical-ever versus latest-common-year coverage.
3. **Do not silently replace the debt source in Phase 1.1.** Make the current scope and both coverage measures visible. Any replacement with IMF WEO general-government gross debt requires a separately reviewed registry/source change and release diff.
4. **World Bank candidate coverage is incomplete.** The World Bank country dimension used by this release does not contain Taiwan. The application may say that selected GDP values share reference year 2025, but must not call the source candidate set globally complete.

### METHODOLOGY PROBLEMS

#### Exact ranking rule

Implement this rule for every metric ranking:

1. The comparison cohort is the current approved analytical universe.
2. `ranking_year` is explicit. The default is the maximum observation year for the selected metric within that cohort and configured release window.
3. Only non-null observations whose `year == ranking_year` participate in the rank.
4. Never fall back to an entity's older observation for ranking.
5. Sort participating observations by value descending, then ISO3 ascending.
6. Assign sequential ordinal ranks `1..N`; equal values do not share rank, and ISO3 determines their order.
7. Entities without an observation in `ranking_year` remain in the table after ranked entities, display `Not available for <ranking_year>`, and receive rank null/`—`.
8. Every ranking response and view must expose `ranking_year`, `ranked_entity_count`, `cohort_size`, and `coverage_ratio`.
9. A separately labelled “latest available value” may be shown for context, with its own observation year, but it must not affect the common-year rank.
10. Historical rank, if later added, must apply the same eligible cohort and exact-year rule for each historical year. Phase 1.1 does not need to add historical rank.

For debt, the default common-year ranking is therefore 2024 with 15 ranked and 35 unranked Top-50 entities. For inflation, the default is 2025; USA and Argentina are unranked for 2025 even though their latest contextual values are from 2024.

#### Observation-year and freshness policy

For annual metrics, compute `lag_years = metric_max_year - latest_observation_year` and expose one structural status:

- `current_year`: lag 0
- `prior_year`: lag 1
- `historical`: lag 2 or more
- `unavailable`: no accepted observation in the configured window

This status describes observation recency relative to the release's metric maximum; it is not an economic-quality judgment and must not use retrieval date as a substitute for observation year. Display the exact observation year and lag alongside the label.

Required fixtures:

- CPI inflation USA: latest 2024, metric maximum 2025, lag 1, `prior_year`, no 2025 rank.
- CPI inflation Argentina: latest 2024, metric maximum 2025, lag 1, `prior_year`, no 2025 rank.
- A debt economy with a 2024 observation: `current_year` relative to debt maximum 2024 and eligible for the 2024 debt rank.
- Germany debt: latest 1990, lag 34 relative to 2024, `historical`, no 2024 debt rank.
- China debt: no observation, `unavailable`, no rank.

#### Analytical-entity eligibility policy

Add an explicit, reviewed registry field; do not infer sovereignty or eligibility from names, regions, ISO-like codes, or World Bank aggregate flags.

Required entity fields:

- `analytical_entity_id` — stable internal ID
- `analytical_eligibility` — `included`, `excluded`, or `pending_review`
- `eligibility_policy_version`
- `eligibility_basis` — concise reviewed rationale
- `effective_from` and optional `effective_to`
- `review_owner`
- `authoritative_ids` object, allowing `world_bank_code`, `imf_weo_code`, `iso3`, and `un_m49` when actually assigned by those authorities
- `source_references` — authoritative registry/document URLs or identifiers

Only `included` entities may enter the ranking candidate pool. `pending_review` and unmapped entities must be excluded with an explicit machine-readable reason. Codex must not assign geopolitical classifications. Seed values require an economist-approved eligibility file; engineering may validate and consume it.

Taiwan must have an explicit reviewed record. Because the current World Bank source has no Taiwan GDP observation/code, Phase 1.1 must either:

- use a separately approved authoritative GDP source mapping for Taiwan and disclose the cross-source comparison, or
- mark it `pending_review`/source-unavailable and disclose that the Top-50 candidate universe is incomplete.

Do not manufacture a World Bank identifier or treat common-year World Bank coverage as resolution of this issue.

### IMPLEMENTATION PROBLEMS

1. Move ranking calculation to a single production data/service layer shared by payloads and UI. The frontend must render provided ranks rather than independently recomputing latest-value ranks.
2. Implement production universe selection through an importable function used by `gei.pipeline.build`; avoid maintaining behavior only inside the build procedure.
3. Preserve exact-year ranking metadata in static shards/exports: `ranking_year`, `observation_year`, rank, cohort size, ranked count, coverage ratio, eligibility status, and missing reason.
4. Add debt coverage fields with unambiguous names: `ever_observed_country_count`, `ranking_year_observed_country_count`, `missing_all_years_country_count`, and `ranking_year_missing_country_count`.
5. Preserve source indicator, raw lineage, release ID, and registry fingerprints. No interpolation, carry-forward, or modeled fallback is authorized.
6. Correct documentation/UI claims so “same-year Top-50 selection” and “candidate-universe completeness” are separate statements.

### TESTING PROBLEMS

1. Replace or relocate the misleading universe tests so Phase 1.1 directly imports and executes the production function used by `gei.pipeline.build`. Tests that intentionally cover `pipelines.build` must be labelled legacy.
2. Add production-path tests for:
   - latest eligible common GDP year selection;
   - aggregate exclusion plus explicit analytical eligibility;
   - deterministic GDP/ISO3 tie ordering;
   - exact 50-entity selection from approved candidates;
   - explicit handling of Taiwan/source-unavailable candidates;
   - no fallback to older values in metric ranks;
   - null rank and deterministic placement for ranking-year missing values;
   - debt 35-ever versus 15-in-2024 coverage definitions;
   - USA and Argentina inflation freshness/ranking cases;
   - registry validation rejecting absent or invalid eligibility states.
3. Add an integration assertion that the universe function tested is the callable invoked by `gei.pipeline.build`.
4. Add DOM or rendered-output checks for ranking year, observation year, missing state, coverage denominator, and freshness label.
5. Do not add hard-coded economic value assertions beyond release-bound fixtures and approved registry contracts.

### PRODUCT/UX PROBLEMS

1. Ranking pages must lead with `Ranking year <year>` and `<ranked>/<cohort> economies have observations`.
2. Keep all cohort entities visible. Missing ranking-year values appear after ranked rows with no rank and an exact missing-state message.
3. If latest historical context is shown, visually separate it from the ranked value and label its observation year.
4. Debt UI must say `Central government debt`, show source/indicator, show `15/50 observed in ranking year 2024`, and separately show `35/50 have any historical observation`.
5. Universe methodology must state: `GDP ranking uses a common 2025 World Bank observation year for source-covered candidates. The candidate universe follows eligibility policy <version> and may exclude entities unavailable from the GDP source.`
6. Surface eligibility/source-unavailable exclusions in methodology or diagnostics without presenting engineering inference as geopolitical fact.

## Required deliverables

1. Versioned analytical-entity eligibility schema and validated, economist-approved registry input.
2. Production common-year ranking module used by `gei.pipeline.build` and frontend payloads.
3. Explicit annual freshness metadata and the required USA/Argentina/debt fixtures.
4. Updated data contracts, methodology, UI copy, diagnostics, and exports.
5. Production-path unit, integration, data-quality, and rendered-UI tests.
6. Release diff and refreshed audit bundle showing both historical-ever and ranking-year coverage.

## Acceptance criteria

- No ranking mixes observation years.
- No older observation silently fills a ranking-year gap.
- Debt coverage reports cannot conflate 35-ever with 15-in-2024.
- The approved eligibility registry, not programmatic sovereignty inference, controls candidate inclusion.
- Taiwan/source-unavailable handling is explicit and test-covered.
- Tests execute the actual universe-selection function called by `gei.pipeline.build`.
- Release metadata and lineage remain intact.
- All existing configuration, production-payload, regression, build, and accessibility checks pass.

## Out of scope

- Phase 2 metrics or features
- Forecasting, scoring, or ML
- Automatic geopolitical classification
- Interpolation or carry-forward ranking values
- An unreviewed debt-source replacement
