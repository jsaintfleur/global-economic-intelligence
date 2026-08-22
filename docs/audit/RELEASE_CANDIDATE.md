# Worldwide Remediation Release Candidate

Release: `release_770e0ce265f624e2a214`
Release code-commit basis: `56cf760a0c1bc5903249a791e31f938339ebed93`

## Scope and counts

- Worldwide governed ingestion universe: **195 entities**.
- Materialized current display cohort: **Top 50**.
- Canonical observations: **51,409** across **8 metrics** and **2 sources**.
- Current rankings: exact-year comparisons within the materialized Top-50 cohort.
- Historical rankings: exact-year comparisons within the contemporaneous governed ingestion universe. Atlas does not project today's Top 50 backward.

## Observation integrity

- Ranking rows preserve observation year, class, source, vintage, coverage state, and missing reason.
- Observation classes present: `actual` (43,865), `estimate` (6,745), `projection` (799).
- Missing reasons are explicit; no missing value is converted to zero.
- Economy GDP share uses an exact-year country numerator and the same-year Top-50 denominator. The interface names that year.

## Governance

Enforcement audit: **17 PASS / 1 WEAK / 0 VACUOUS / 0 MISBOUND**.

- `D-003` / `TEST-E-002` — A future adapter refactor could weaken the explicit unknown-code failure without this test detecting it. Owner: Phase 1.1 adapter hardening. Remediation: Add a synthetic gzipped SDMX fixture containing an undeclared code and assert that read_metric_fixture_observations fails closed. Public release blocker: false. Map/Phase 2 blocker: true.

## Geographic readiness

**World map is not implemented because geographic governance is incomplete.** Zero entities are currently renderable. The readiness audit records **50 missing geometry** and **145 missing geographic governance**. Atlas does not imply partial geographic coverage.

## Scale and performance

- Initial browser catalog: **122,990 bytes**.
- Canonical store: **43,207,214 bytes**; it is not deployed as an initial browser payload.
- Worldwide ranking shards: **8 lazy assets**, **47,842,064 bytes** total.
- Static production build: **134 assets**, **75,846,079 bytes**.

Machine-readable evidence: [`release_candidate_evidence.json`](../../data/audit/release_770e0ce265f624e2a214/release_candidate_evidence.json).
