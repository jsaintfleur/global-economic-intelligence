# Atlas Product and Visualization Audit

Date: 2026-08-22
Scope: Phase 1.1 approved Top-50 release and premium preview
Constraint: preserve the current Manrope type system and blue-gradient product palette.

## Current visual strengths

- Strong editorial masthead, consistent hierarchy, restrained spacing, and credible source language.
- Cohort year, coverage, missingness, and provenance are visible rather than hidden.
- Overview, rankings, profiles, comparison, scatter, coverage, and methodology share one interaction model.
- Light and dark themes are coherent and responsive behavior is already stable.

## Current visual weaknesses

- Country identity is mostly textual; users cannot build visual memory across tables, search, profiles, and charts.
- Multi-series charts assign colors by selection order, so the same economy changes identity between views.
- Line paths connect across missing years and can imply continuity that the observations do not support.
- Charts lack publication footnotes and presentation-ready SVG export.
- Comparison legends are detached from deterministic country identity and do not identify gaps.
- The Overview is strong editorially but geographically silent; no approved geometry registry exists yet.
- Repeated cards and borders remain heavier than necessary on dense analytical pages.

## Component disposition

| Component | Decision | Reason |
|---|---|---|
| Editorial masthead | KEEP | Clear product proposition and hierarchy. |
| GDP treemap | REFINE | Strong overview device; needs scalable cohort/year controls and fallback table. |
| Ranking tables | REFINE | Economically sound; improve identity, filtering, and density. |
| Multi-country lines | REBUILD | Must preserve gaps, deterministic identity, direct end labels, and export metadata. |
| Scatter explorer | REFINE | Strong descriptive tool; improve identity and high-density focus behavior. |
| Inflation distribution | REFINE | Useful context; needs robust outlier scaling in a later pass. |
| Coverage table | REFINE | Transparent but not geographic; retain until governed geometry is available. |
| Decorative dashboard cards | REMOVE/REDUCE | Prefer explanatory figures and compact evidence strips. |

## Global-scaling risks

- D-002 remains binding for Phase 1.1; worldwide comparison-year policy is not yet approved.
- A worldwide universe requires explicit eligibility adjudication, not source-code shape inference.
- Region and income cohorts may only use authoritative committed metadata.
- Search and tables scale readily; SVG scatter, profiles, and map joins require explicit scale tests.
- Missing geometry, missing observations, excluded entities, and join failures must remain distinct states.

## Recommended map architecture

- Commit a versioned Natural Earth geometry snapshot separately from economic observations.
- Join only through an explicit governed entity-to-geometry registry.
- Fail closed on unknown joins and publish an adjudicated unmappable-entity list.
- Use metric-semantic scales: sequential for levels, zero-centered diverging for signed changes, and separately reviewed risk scales.
- Provide keyboard-accessible geographic targets plus a synchronized searchable table.
- Do not ship a choropleth until the geometry registry and TEST-W-007-style missing/join distinction are approved.

## Recommended chart architecture

- Retain the lightweight SVG system for Phase 1.1; it is crisp, dependency-free, exportable, and adequate at this scale.
- Centralize country identity, gap-aware path construction, annotations, tooltips, and export metadata.
- Re-evaluate canvas or hybrid rendering only after the 200-economy × 100-metric scale harness demonstrates a bottleneck.

## Country identity and color system

- Curated, flag-inspired colors for commonly compared economies.
- Deterministic accessible fallback palette for every approved entity.
- Collision avoidance when selected series share a primary color.
- Country name, direct labels, focus states, and tooltips remain mandatory; color is never the sole identifier.
- Flags require an explicit ISO2/asset mapping and a visible fallback for non-standard analytical entities.

## Highest-impact safe changes

1. Deterministic country identity across comparisons, profiles, rankings, scatter, and search.
2. Gap-aware publication-grade line charts with direct end labels and exact-value focus targets.
3. Compact chart footnotes with source, unit, year range, coverage, and release lineage.
4. SVG and CSV export from the analytical figure itself.
5. Approved-region filtering architecture without changing the governed Top-50 product boundary.
6. Geometry registry and worldwide universe remain explicit Phase 2 dependencies.

## Scale-test result

The synthetic harness measured 200 economies × 100 metrics × 30 years (600,000 observations) at 122,987,091 serialized bytes, 6.410 seconds generation, 7.815 seconds serialization, and 480.6 MB peak memory on the audit machine. A monolithic worldwide payload is therefore rejected. The existing catalog plus lazy metric/profile/ranking shard architecture is the required global-scale path; maps and search should consume compact dedicated indexes rather than the observation corpus.
