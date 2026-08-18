# Test Coverage Map

Technical summary: 37 tests protect structural contracts; one explicit registry assertion protects the current debt-scope economic contract. The suite does not supply independent economic approval.

| Test file | Test | Invariant | Class | Metrics |
| --- | --- | --- | --- | --- |
| tests/contracts/test_adapter_contract.py | test_identity_and_snapshot_contract | Raw snapshot preservation and checksum | structural | all Phase 1 metrics |
| tests/contracts/test_adapter_contract.py | test_country_ingest_contract | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/data_quality/test_production_payload.py | test_payload_is_structurally_valid | Published payload contract, provenance, uniqueness, and Top-50 shape | structural | all Phase 1 metrics |
| tests/integration/test_pipeline.py | test_pipeline_is_deterministic_from_identical_inputs_and_writes_manifest | Deterministic pipeline outputs and manifest | structural | all Phase 1 metrics |
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
| tests/test_universe.py | test_reference_year_uses_latest_complete_year | Universe reference-year completeness rule (legacy `pipelines.build` path) | structural | gdp_current_usd |
| tests/test_universe.py | test_gdp_ranking_descending_and_limited | GDP descending Top-N universe selection (legacy `pipelines.build` path) | structural | gdp_current_usd |
| tests/test_universe.py | test_world_bank_aggregates_are_excluded | World Bank aggregate records excluded (legacy `pipelines.build` path) | structural | gdp_current_usd |
| tests/unit/test_adapter.py | test_raw_snapshot_is_preserved_with_checksum | Raw snapshot preservation and checksum | structural | all Phase 1 metrics |
| tests/unit/test_adapter.py | test_cache_avoids_network | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_schema_change_is_detected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_rate_limit_and_server_error_are_retried_without_slow_test | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_timeout_connection_failure_and_invalid_json_surface_after_retries | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_partial_and_empty_schema_are_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
| tests/unit/test_adapter.py | test_unsafe_indicator_filename_is_rejected | Implementation behavior named by test; inspect test body for exact assertion | structural | as applicable |
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

- The three tests in `tests/test_universe.py` target legacy `pipelines.build`, not the current production `gei.pipeline.build` universe path.
- No independently economist-approved expected-value fixtures for any Phase 1 metric.
- No test asserts a common-year mode for non-universe metric rankings because that mode is not implemented.
- No test defines a shared-rank policy for ties in UI metric tables.
- No automated DOM assertion covers every page/metadata field in the UI visibility matrix.
- No sovereign-state/territory classification invariant exists; the registry deliberately leaves it null.
- No historical-rank invariant exists because historical rank is not implemented.

Machine map: [`test_coverage_map.csv`](../../data/audit/release_e9182edbdb3e275e19ca/test_coverage_map.csv).
