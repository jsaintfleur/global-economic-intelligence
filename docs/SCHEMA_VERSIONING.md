# Schema versioning

Versioned contracts currently include Canonical Observation 2.0, Metric Registry 1.0, Source Registry 1.0, Transformation Registry 1.0, Country Registry 1.0, Pipeline Manifest 1.0, Coverage Matrix 1.0, Snapshot Diff 1.0, Regression Report 1.0, and Data Release 1.0.

Additive optional fields may ship in a minor contract revision. Removing or renaming fields, changing identity keys, changing value types, or altering semantics requires a new major version and an explicit migration note. Readers must reject unsupported major versions rather than guessing.

Registry content versions are SHA-256-derived and recorded in each release manifest. Contract versions describe shape; registry versions identify exact declarations.

Migration order is raw snapshot → source normalizer → canonical observation → registry join → validation → analytical output. Raw evidence must remain readable through a migration even when normalized artifacts are rebuilt.
