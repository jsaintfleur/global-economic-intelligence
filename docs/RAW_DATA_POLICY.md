# Data storage and retention

- Commit source/metric/transformation registries, small release manifests, tests, and engineering fixtures.
- Do not commit raw API responses or release snapshot archives. They are reproducible evidence artifacts but grow without bound and belong in versioned object storage for production.
- Commit deployable `app/data` assets only when the repository is serving as the release artifact. They let a clean checkout run offline.
- Do not commit `data/processed` working outputs, diffs containing full observation keys/revisions, or `dist/`.
- Preserve raw snapshots locally by retrieval date and SHA-256. Never overwrite or delete evidence as part of a routine refresh.
- A future archival store should retain raw snapshots and release snapshots by immutable ID, with lifecycle policy managed outside Git.

The `.gitignore` implements these boundaries without deleting existing local evidence.
