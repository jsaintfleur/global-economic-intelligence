# governance/

Decisions that bind the pipeline live here as files, not as prose in a handoff document.

## Why this directory exists

Phase 1.1 shipped a universe ranked on the wrong source. The cause was not a bad
implementation — it was that decision **D-001** and test **TEST-U-002** existed only in
handoff prose and had no representation in the repository. PR #2 did not violate a
decision; it never received one.

Diagnosis, precisely: `CLAUDE_TO_CODEX.md` (the Phase 1.1 spec) does not itself contain
`TEST-U-002`. It carries the line *"All Phase-1 blocking tests remain in force"*, and
`TEST-U-002` is defined one document upstream in `CLAUDE_TO_CODEX_PHASE_1.md`. A
requirement reachable only by following a cross-document reference is a requirement that
will eventually be missed. It was.

## Contract

1. **One file per decision**, `decisions/D-NNN.yaml`. Append-only: superseding means adding
   a new record that names the one it replaces, never editing in place.
2. **Tests declare the decision they enforce** with a machine-readable marker
   (`@decision("D-001")`). A comment saying "per D-001" does not count.
3. **`TEST-G-001` closes the loop in both directions** — every active decision has an
   enforcing test, and every marker resolves to an active decision.
4. **Handoffs ship decision files as content to be committed**, not narrative to be
   transcribed. If a rule arrives only as prose, it is not in force.

## Status of the backfill

`D-001` … `D-013` in this directory are transcribed from `out/agent_handoff/DECISIONS.md`.
Until each is committed **and** covered by `TEST-G-001`, treat it as **not in force**. Do
not retro-apply any of them from memory of earlier handoff documents — that is the exact
failure mode this directory exists to end.

Two records carry amendments made on 2026-08-22:

- **D-001** — rationale previously named Iraq as the World Bank cohort's #50. Corrected by
  Codex: the WB **2025** cohort ends with Algeria at #50, Iraq at #53. The original figure
  came from WB **2024** with the reference year left unstated. The rationale no longer names
  a promoted economy at all, because that identity is reference-year dependent and therefore
  not a stable premise.
- **D-002** — the ">=95% actual" threshold was ambiguous between cohort-scoped and
  pool-scoped. It is **cohort-scoped**. At reference year 2024 the selected 50 are 100%
  actual while the 195-economy candidate pool is 87% (169/195). Also adds the fiscal-year boundary form
  (`FY2024/25`), which was previously unspecified and breaks any integer cast.

## fixtures/

`weo_universe_2026-04-14.json` pins the expectations for `TEST-U-002` / `002b` / `002c`
against a named WEO vintage. When the vintage changes the test must **fail loudly** and a
human must re-pin. A fixture that regenerates itself asserts nothing.
