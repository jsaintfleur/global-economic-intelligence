# Test Coverage Map

Technical summary: 50 tests protect structural contracts; one explicit registry assertion protects the current debt-scope economic contract. The suite does not supply independent economic approval.

| Test file | Test | Invariant | Class | Metrics |
| --- | --- | --- | --- | --- |
| tests/contracts/test_adapter_contract.py | test_identity_and_snapshot_contract | Raw snapshot preservation and checksum | structural | all Phase 1 metrics |
| tests/contracts/test_adapter_contract.py | test_country_ingest_contract | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/data_quality/test_phase_1_1_release.py | test_inflation_missing_2025_is_not_backfilled | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/data_quality/test_phase_1_1_release.py | test_debt_ever_observed_and_same_year_coverage_are_distinct | Coverage matrices and metric inventory grains | structural | all Phase 1 metrics |
| tests/data_quality/test_phase_1_1_release.py | test_same_year_gdp_does_not_imply_complete_candidate_universe | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/data_quality/test_production_payload.py | test_payload_is_structurally_valid | Published payload contract, provenance, uniqueness, and Top-50 shape | structural | all Phase 1 metrics |
| tests/integration/test_pipeline.py | test_pipeline_is_deterministic_from_identical_inputs_and_writes_manifest | Deterministic pipeline outputs and manifest | structural | all Phase 1 metrics |
| tests/legacy/test_legacy_universe.py | test_legacy_reference_year_contract | Universe reference-year completeness rule | structural | gdp_current_usd |
| tests/test_frontend_contract.py | test_exact_year_missing_state_and_historical_context | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/test_frontend_contract.py | test_url_state_and_coverage_are_first_class | Coverage matrices and metric inventory grains | structural | all Phase 1 metrics |
| tests/test_frontend_contract.py | test_export_contains_lineage | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/test_metrics.py | test_registry_is_structurally_valid | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/test_metrics.py | test_metric_ids_are_unique | Metric registry fields and uniqueness | structural | all Phase 1 metrics |
| tests/test_metrics.py | test_every_metric_has_canonical_fields | Metric registry fields and uniqueness | structural | all Phase 1 metrics |
| tests/test_metrics.py | test_debt_definition_remains_central_government | Debt registry remains central-government scoped | economic-contract | central_government_debt_pct_gdp |
| tests/test_quality.py | test_built_payload_contract_if_present | Published payload contract, provenance, uniqueness, and Top-50 shape | structural | all Phase 1 metrics |
| tests/test_transformations.py | test_cagr | CAGR formula behavior | structural | mechanism only |
| tests/test_transformations.py | test_pct_change | Percentage-change formula behavior | structural | mechanism only |
| tests/test_transformations.py | test_rank_desc_is_deterministic_and_missing_visible | Deterministic descending ranks and visible missing rank | structural | all Phase 1 metrics |
| tests/test_transformations.py | test_latest_by_country_uses_each_country_latest_not_global_year | Latest available year selected independently by country | structural | all Phase 1 metrics |
| tests/test_transformations.py | test_rebase_preserves_missing_values | Rebase formula preserves missing values | structural | mechanism only |
| tests/test_universe.py | test_latest_complete_year_uses_production_function | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/test_universe.py | test_ties_use_iso3_and_nonincluded_entities_are_excluded | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/test_universe.py | test_exact_top_n_selection | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_raw_snapshot_is_preserved_with_checksum | Raw snapshot preservation and checksum | structural | all Phase 1 metrics |
| tests/unit/test_adapter.py | test_cache_avoids_network | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_schema_change_is_detected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_rate_limit_and_server_error_are_retried_without_slow_test | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_timeout_connection_failure_and_invalid_json_surface_after_retries | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_partial_and_empty_schema_are_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_unsafe_indicator_filename_is_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_analytics.py | test_exact_year_ranking_has_no_historical_fallback | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_analytics.py | test_recency_classification | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_analytics.py | test_historical_rank_is_within_same_year_cohort | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_analytics.py | test_indexed_trajectory | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_analytics.py | test_metric_specific_changes | Metric registry fields and uniqueness | structural | all Phase 1 metrics |
| tests/unit/test_analytics.py | test_country_profile_reports_latest_recency_and_same_year_rank | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_coverage.py | test_all_matrix_grains_and_inventory | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_diff.py | test_value_revision_has_absolute_and_percent_change | Release diff revision calculations | structural | all Phase 1 metrics |
| tests/unit/test_diff.py | test_structural_and_source_changes_are_reported | Source mapping changes are reported | structural | all Phase 1 metrics |
| tests/unit/test_diff.py | test_machine_and_human_outputs_are_written | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_normalization.py | test_country_normalization_excludes_aggregates | World Bank aggregate records excluded | structural | gdp_current_usd |
| tests/unit/test_normalization.py | test_provenance_propagates_and_ids_are_stable | Lineage fields propagate and are required | structural | all Phase 1 metrics |
| tests/unit/test_normalization.py | test_malformed_partial_and_duplicate_records_are_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_release_regression.py | test_release_id_is_content_deterministic | Content-derived release and regression controls | structural | all Phase 1 metrics |
| tests/unit/test_release_regression.py | test_missing_provenance_is_blocking | Lineage fields propagate and are required | structural | all Phase 1 metrics |
| tests/unit/test_release_regression.py | test_value_revisions_do_not_block | Release diff revision calculations | structural | all Phase 1 metrics |
| tests/unit/test_validation.py | test_duplicate_metric_ids_are_rejected | Metric registry fields and uniqueness | structural | all Phase 1 metrics |
| tests/unit/test_validation.py | test_duplicate_observation_key_is_rejected | Canonical observation identity and key integrity | structural | all Phase 1 metrics |
| tests/unit/test_validation.py | test_orphan_and_invalid_iso_are_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |

## Important uncovered areas

- No independently economist-approved expected-value fixtures exist beyond the audited release cases.
- No automated DOM assertion covers every page and metadata field; browser QA remains required.
- Analytical eligibility is explicit, but source expansion for Taiwan remains pending economic review.

Machine map: [`test_coverage_map.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/test_coverage_map.csv).
