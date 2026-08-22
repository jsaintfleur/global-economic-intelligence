# Change classification

- **Application change** — UI, pipeline implementation, validation, performance, packaging, or documentation without registry meaning changes.
- **Data change** — observation additions, removals, or revisions under unchanged metric/source declarations.
- **Metric definition change** — description, unit, transformation, missing-data rule, or interpretation changes in the metric registry.
- **Source change** — source organization, dataset, indicator mapping, adapter, or retrieval contract changes.
- **Methodology change** — universe construction, comparability rule, derived measure, weighting, modeling, or interpretive policy changes.

Release notes should use these headings explicitly. Snapshot diffs describe data changes; registry hashes and source-mapping diffs distinguish definition/source changes from ordinary refreshes.

When coverage changes because a metric's institutional scope or primary source changes,
release notes must state that cause explicitly and must not imply that newly covered entities
started reporting. Phase-specific required disclosures live under `docs/releases/`.
