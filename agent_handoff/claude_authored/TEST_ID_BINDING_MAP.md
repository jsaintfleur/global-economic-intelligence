# Binding the governed test IDs — most of TEST-G-002's list is labelling, not writing

**Filed:** 2026-08-22 · Claude (Agent A) · Input for remediation step 1.

`TEST-G-002` enumerating ~20 missing stable test IDs reads like twenty tests to write. It
mostly is not. The existing suite already implements most of these behaviours under different
names; what is missing is the `@pytest.mark.test_id(...)` label that binds them to a decision.
Reading the list as a writing task would duplicate coverage that already exists.

## Already implemented — attach the marker, write nothing

| Test ID | Decision | Existing implementation |
|---|---|---|
| `TEST-U-001` | D-003 | `test_country_normalization_excludes_aggregates` |
| `TEST-U-004` | D-005 | `test_historical_rank_is_within_same_year_cohort` |
| `TEST-U-005` | D-002 | `test_exact_year_ranking_has_no_historical_fallback`, `test_latest_by_country_uses_each_country_latest_not_global_year`, `test_inflation_missing_2025_is_not_backfilled` |
| `TEST-F-001` | D-002 | `test_recency_classification`, `test_country_profile_reports_latest_recency_and_same_year_rank` |
| `TEST-T-001` | D-006 | `test_raw_snapshot_is_preserved_with_checksum`, `test_duplicate_observation_key_is_rejected` |
| `TEST-T-002` | D-006, D-012 | `test_provenance_propagates_and_ids_are_stable`, `test_release_id_is_content_deterministic` |
| `TEST-R-001` | D-007, D-013 | `test_rank_desc_is_deterministic_and_missing_visible` |
| `TEST-R-002` | D-008 | `test_ties_use_iso3_and_nonincluded_entities_are_excluded` |
| `TEST-E-002` | D-003 | `test_orphan_and_invalid_iso_are_rejected` (partial — extend for `consolidated_into`) |

Where several tests cover one ID, mark them all. `TEST-G-002` requires the ID to exist in the
session, not to be unique.

## Genuinely missing — write these

`TEST-U-002` / `002b` / `002c` (D-001, the pinned universe), `TEST-U-003` (WB cross-check
delta ≤ 2), `TEST-C-001` (comparability class governs UI capability, not tooltip text),
`TEST-E-001` / `E-003` (eligibility gate and the no-inference assertion), `TEST-F-002` /
`F-003` (source substitutions and the exclusion list).

## Two existing tests contradict active decisions

These are the same class as the Taiwan assertion Codex found, and they will fight the
remediation rather than fail cleanly beside it:

- **`tests/test_metrics.py:21`** — `test_debt_definition_remains_central_government` asserts
  the debt metric is `central_government_debt_pct_gdp` with *"Central government"* in the
  display name. **D-008** moves debt to WEO `GGXWDG_NGDP` (general government) and **D-009**
  removes `GC.DOD.TOTL.GD.ZS` entirely. This test pins the metric D-008 replaces.
- **`tests/data_quality/test_phase_1_1_release.py:31`** —
  `test_same_year_gdp_does_not_imply_complete_candidate_universe`, already identified: it
  encodes `candidate_universe_complete: false` and Taiwan's exclusion, both of which D-001
  reverses.

Both must be corrected **in the same commit** as the decision they contradict. Split across
commits, one of them is red by construction — and a red test with a plausible name is
exactly what gets "fixed" by reverting the decision instead of the test.

## A schema defect in my decision files

`TEST-G-001` requires every `status: active` decision with a non-empty `enforced_by` to have a
binding test. Four decisions cannot satisfy that yet, because the features they govern do not
exist in Phase 1.1:

- **D-010** — inequality metrics barred from composites. *There are no composites.*
- **D-011** — composite scores publish a rank interval. *Same.*
- **D-012** — forecast benchmark is WEO at matching horizon. *No forecasting.*
- **D-013** — "Growth Drivers" renamed "Historical Associations". *No such module.*

These are real decisions, correctly adopted, that govern future work. Forcing a test to exist
would mean writing a test for absent code — and the natural way to make such a test pass is to
weaken it until it asserts nothing.

**Fix:** add a third status value.

```yaml
status: adopted_pending_implementation
```

`TEST-G-001` skips these for the enforcement check but still requires that they parse, that
their IDs are unique, and that no test references them yet. When the feature lands, the
status flips to `active` in the same commit that adds the test. Amend D-010 through D-013 to
this status now; D-001–D-009 stay `active`.

This is my error, not Codex's: I wrote `enforced_by` lists for decisions whose features had
not been built, and `TEST-G-001` correctly refused to accept the inconsistency.
