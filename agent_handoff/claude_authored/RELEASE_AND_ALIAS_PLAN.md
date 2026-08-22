# Atlas — production alias plan

**Status:** alias deliberately NOT created. **Owner of execution:** Codex.
**Filed:** 2026-08-22 by Claude (Agent A)

## Why there is no alias yet

Checked against the Vercel account `jsaintfleurs-projects` (`team_0ugDlvWrFPBi8GJUcrMVnZlg`):

- **No Atlas project exists.** Atlas has never been deployed. There is nothing to alias.
- `econos` production currently serves commit `dc0459b`, *"chore: move canonical domain to
  econos.jeanlucs.com"* — the EconOS US FRED/BLS dashboard from April. A different product.
  Promoting anything Atlas-shaped into that alias destroys a live site.
- The only Atlas-adjacent build that exists is the `atlas-datalab` preview
  (`econos-kmfw09wqb-…`, `target: null`). It is computed over the World Bank universe that
  omits Taiwan, and Codex has already correctly rejected it as not-Atlas.

Producing a production alias today would publish, under a production URL, a Top-50 that is
wrong on its central claim. That is the precise failure the last three exchanges were spent
containing. **Decision: hold.**

## Preconditions for the alias

Every one of these must be green before an Atlas production alias is created:

1. `governance/` committed; `TEST-G-001` and `TEST-G-002` pass.
2. Handoff divergence adjudicated (`agent_handoff/claude_authored/README_DIVERGENCE.md`) —
   one controlling `CLAUDE_TO_CODEX` document, not two.
3. Universe provider is `imf_weo`, ranked on `NGDPD`, actual observations only.
4. `TEST-U-002` / `002b` / `002c` pass against the **production pipeline and release
   payload**, on the pinned vintage `2026-04-14`: Taiwan at rank 22, KAZ in at #50, IRQ out
   at #51, five fiscal-year reporters classified actual at 2024.
5. `candidate_universe_complete: true` in the payload.
6. Full derived-asset rebuild per remediation §8.1 — ranks, percentiles, peers, coverage,
   aggregates, insights, maps, profiles — with the release-ID consistency assertion passing.
7. All 24 blocking tests green.
8. Design loop restarted from the top and completed against the corrected universe.

Steps 1–7 are correctness. Step 8 is the one most likely to be skipped under time pressure,
and it is the one that determines whether Atlas reads as a product or as a data dump.

## Recommended alias shape

- **Project:** create a dedicated `atlas` project. Do **not** reuse `econos` — the two are
  different products and sharing a project makes the rollback history incoherent.
- **Domain:** `atlas.jeanlucs.com`. The account already serves `econos.jeanlucs.com`, so this
  needs no purchase and no new DNS zone — one CNAME.
- **Sequence:** preview alias first (`atlas-preview.jeanlucs.com`), design loop runs there,
  production alias assigned only after step 8.
- **Link it to git, do not hand-deploy files.** The repo has a GitHub remote
  (`jsaintfleur/global-economic-intelligence`) with `main`, `agent/phase-1-1` and
  `agent/atlas-premium-product` pushed. Create the project *linked to that repo* so every
  Atlas deployment originates from a commit Codex pushed. This makes the standing rule below
  structural rather than procedural: a build with no commit behind it cannot exist.

## Blocker diagnosis — Vercel project creation (2026-08-22)

Reproduced twice, both paths, same account:

| path | result |
|---|---|
| `deploy_to_vercel` (file deploy, new project `perm-probe-0822`) | `403 forbidden` — *"You don't have permission to create a project."* |
| `create_git_project` (git-linked, project `atlas`) | `403 forbidden` — *"You don't have permission to create the project."* with `"action":"create","resource":"project"` |

Meanwhile `list_teams`, `list_projects`, `list_deployments` and **deploying into the existing
`econos` project** all succeed on the same credential.

**That asymmetry is the diagnosis.** The credential has read and deploy rights on projects
that already exist and no `create` right on the `project` resource. Per Vercel's OAuth
documentation, an app or token can be installed scoped to a named subset of projects
(`vercel oauth-apps install --client-id … --projects prj_a,prj_b`), which produces exactly
this behaviour. It is **not** a plan limit — `hobby` allows well over the 19 projects on the
account — and it is not a team-role problem, since the account owner is the only member.

**Fix (user action, not Codex):** reconnect the Vercel integration granting **All Projects**
rather than a selected subset, or issue a token that is not project-scoped. Then re-run
either probe above; a 200 means step 5 is unblocked.

Do this before the release window. It is the only blocker on the critical path that no amount
of correct code will clear, and discovering it at deploy time turns a green gate into a stall.

## Standing rule

Codex owns Atlas deployments. Any URL presented as Atlas that did not come from Codex's build
of a merged, gate-passing commit should be rejected on sight — including any produced by me.
That rule exists because I produced one, and it was right to reject it.
