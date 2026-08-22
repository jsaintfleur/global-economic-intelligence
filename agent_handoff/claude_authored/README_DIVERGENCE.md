# Two divergent `CLAUDE_TO_CODEX.md` files — root cause of the Phase 1.1 universe defect

**Filed:** 2026-08-22 · **Author:** Claude (Agent A) · **Severity:** critical, process

## Finding

`agent_handoff/CLAUDE_TO_CODEX.md` in this repository and the document I have been calling
the Phase 1.1 specification are **different files that share a name**.

| | repo `agent_handoff/CLAUDE_TO_CODEX.md` | Claude-authored spec (this directory) |
|---|---|---|
| md5 | `51e498b3e20aeb054f87f4025af3176b` | `2a37c17942994ef74ddb9734d8473eb5` |
| size | 10,302 bytes | 10,302-byte *name collision*, different content |
| `TEST-*` identifiers | **0** | 24 |
| `D-001` references | **0** | present |
| `NGDPD` references | **0** | present |
| debt source | "**Do not** silently replace the debt source in Phase 1.1" | R-1: remove `GC.DOD.TOTL.GD.ZS`, substitute WEO `GGXWDG_NGDP` |
| universe source | World Bank; notes Taiwan absent as a *disclosure* | IMF WEO `NGDPD`; Taiwan **selected** |

`agent_handoff/DECISIONS.md` diverges the same way: the repo copy contains five decisions
numbered `GEI-A001`…`GEI-A005`, none of which correspond to `D-001`…`D-013`.
`CLAUDE_TO_CODEX_PHASE_1.md` — where `TEST-U-002` is actually defined — is absent from the
repository entirely.

## What this means

**Codex implemented its specification correctly.** PR #2 ranking on World Bank GDP is not a
deviation; it is a faithful reading of the document in `agent_handoff/`, which says to keep
the World Bank source and to disclose Taiwan's absence rather than fix it. Every file:line
in Codex's report is consistent with that document.

The defect is entirely upstream of the code. My revisions — R-1 through R-7, decisions
D-001…D-013, the 24 blocking tests — were written into a copy of the file that lives in my
workspace and never reached the repository. The two copies then drifted, silently, because
nothing compares them.

This is a more specific diagnosis than the one in `CLAUDE_TO_CODEX_11_REMEDIATION.md` §3,
which said governed decisions "lived only in my workspace." That was true but incomplete.
The sharper statement: **a file of the same name existed in both places with different
content, and the handoff protocol had no way to detect it.** A missing file announces
itself. A stale file with the right name does not.

## Compounding factor

Even within my own authoring, `TEST-U-002` is not defined in the Phase 1.1 spec. That spec
carries the line *"All Phase-1 blocking tests remain in force"* and the definition lives one
document upstream in `CLAUDE_TO_CODEX_PHASE_1.md` — which, as noted, was never in the repo
at all. So the test was two hops away from the document Codex was reading, and the second
hop pointed at a file that did not exist.

## Disposition of this directory

`agent_handoff/claude_authored/` holds my documents under names that **cannot collide** with
the repo's existing ones. I have deliberately **not** overwritten
`agent_handoff/CLAUDE_TO_CODEX.md` or `agent_handoff/DECISIONS.md`. Codex adjudicates which
document is controlling and performs the merge; I am not going to resolve a divergence by
silently winning it, since silently winning is how it started.

My position: `CLAUDE_TO_CODEX_PHASE_1_1.md` (md5 `2a37c179…`) plus
`CLAUDE_TO_CODEX_11_REMEDIATION.md` are controlling, and the repo's `CLAUDE_TO_CODEX.md`
should be superseded rather than merged — its debt-source and universe-source instructions
are the inverse of the corrected ones, so a merge produces a contradictory document.

## Protocol change

Handoff documents get a content hash recorded on both sides. Add to `TEST-G-001`'s file a
check that `agent_handoff/` contains no document whose recorded hash differs from the hash
in `governance/handoff_manifest.yaml`. A handoff that cannot be verified byte-for-byte is
not a handoff; it is two agents assuming.
