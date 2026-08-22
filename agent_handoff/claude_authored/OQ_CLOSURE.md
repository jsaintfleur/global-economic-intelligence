# Open questions — closure (OQ-11-001, OQ-11-002, OQ-11-003)

**Filed:** 2026-08-22 · **Author:** Claude (Agent A) · All three resolved from repository evidence.

---

## OQ-11-002 — "the cited audit paths do not exist" · **WITHDRAWN — my error**

I reported that `docs/audit/README.md` and `data/audit/release_e9182edbdb3e275e19ca/` could
not be found, and raised it as a blocking evidence gap.

Both exist and always did. `docs/audit/` holds 14 documents; the release directory holds 18
artefacts including `phase_1_1_reconciliation.json` and `top50_universe_candidates.csv`.

**Cause:** I was looking in `~/Developer/EconOS`, a different product on the same machine.
The correct repository is `~/Documents/New project/global-economic-intelligence`, which I did
not have access to until today. I reported "the evidence does not exist" when the accurate
statement was "I cannot see the evidence." Those are different claims and I made the stronger
one. Same failure mode as the divergent `CLAUDE_TO_CODEX.md`: **two things with the same
shape in different places, and no check that I was looking at the right one.**

---

## OQ-11-001 — "what query yields 35/50 debt coverage?" · **RESOLVED**

`docs/audit/CURRENT_DEBT_IMPLEMENTATION.md:12`:

> Coverage: 35 of 50 countries, 608 observations, 1990-2024. Missing countries: CHN, JPN,
> FRA, SAU, BEL, IRL, ARG, SWE, AUT, VNM, ROU, HKG, IRN, NGA, DZA.

35 = economies with **at least one** `GC.DOD.TOTL.GD.ZS` observation anywhere in 1990–2024.
15 = economies with an observation **at 2024**, the metric-wide latest year. 35 + 15 named
absentees = 50, and the 608-observation count over a 35-year window is consistent with
historical-ever coverage.

This confirms `AUDIT_RECONCILIATION_11.md` from primary evidence rather than inference. The
two figures were never in conflict; they answer different questions, and neither was labelled
with the question it answered. **D-008 and D-009 stand unchanged** — 35/50 historical-ever
does not rescue a metric that is 15/50 at the comparison year, because rankings are
computed at a pinned year, not over a union of years.

Worth noting which economies are missing: CHN, JPN, FRA. A debt table whose absentees are the
second, third and seventh largest economies is not a table with gaps; it is a different table.

---

## OQ-11-003 — "is `pipelines.build` legacy?" · **RESOLVED: yes, non-production**

Evidence:

- `tests/legacy/test_legacy_universe.py:1` — *"Compatibility coverage for the non-production
  `pipelines.build` module."*
- `Makefile` `data:` target runs `python3 -m gei.pipeline`. Nothing invokes `pipelines.build`.
- `pipelines/` contains only `build.py` (1,865 bytes) and `world_bank.py` (152 bytes).

**Production is `gei.pipeline`.** The remediation applies there and only there. One caution:
`pipelines/build.py` exports `select_reference_year`, which is a *governed* concept under
D-002. A second, unreferenced implementation of a governed rule is a live hazard — someone
will eventually import the wrong one, and it will not be obvious. Either delete it or mark it
`DEPRECATED — see D-002` at module level. It should not simply be left alone.

---

## Remaining open

**OQ-11-004** — eligibility adjudication is complete for ranks 1–65 plus named exceptions
(`governance/entities/eligibility_adjudication.yaml`). Entities outside that range remain
unadjudicated by design; they cannot reach the universe, and R-5.2's gate will surface any
that ever do.
