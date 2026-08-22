# Schema versioning

Versioned contracts currently include Canonical Observation 2.0, Metric Registry 1.0, Source Registry 1.0, Transformation Registry 1.0, Country Registry 1.0, Pipeline Manifest 1.0, Coverage Matrix 1.0, Snapshot Diff 1.0, Regression Report 1.0, and Data Release 1.0.

Additive optional fields may ship in a minor contract revision. Removing or renaming fields, changing identity keys, changing value types, or altering semantics requires a new major version and an explicit migration note. Readers must reject unsupported major versions rather than guessing.

Registry content versions are SHA-256-derived and recorded in each release manifest. Contract versions describe shape; registry versions identify exact declarations.

Migration order is raw snapshot → source normalizer → canonical observation → registry join → validation → analytical output. Raw evidence must remain readable through a migration even when normalized artifacts are rebuilt.

## Metric identity and definition migrations

A change in institutional scope creates a new metric identity even when the unit and broad
topic remain similar. In particular,
`central_government_debt_pct_gdp` and
`general_government_gross_debt_pct_gdp` are distinct series: general government consolidates
central, state or local, and social-security entities. A release adopting IMF WEO
`GGXWDG_NGDP` must therefore remove the former metric and add the latter. It must not rewrite
the old metric's history or classify the change as an observation revision.

A compiler or provider change that preserves the economic definition may retain its metric
ID, but the snapshot diff must report a structural `source_mapping_change`. Nominal GDP
moving from World Bank `NY.GDP.MKTP.CD` to IMF WEO `NGDPD` is the canonical example.
