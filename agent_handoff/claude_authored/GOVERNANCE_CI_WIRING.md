# TEST-G-001 will not run under the current CI — required patch before committing `governance/`

**Filed:** 2026-08-22 · Claude (Agent A) · **Blocking for step 1 of the remediation sequence.**

## The defect

Codex's condition — *"the full CI workflow including the governance suite must be a required
branch-protection check"* — cannot be satisfied by the repository as configured. Four separate
mechanisms each independently prevent the governance suite from executing:

| # | Mechanism | Effect |
|---|---|---|
| 1 | `Makefile` `test:` runs `python3 -m unittest discover -s tests` | Scans `tests/` only. `governance/tests/` is never reached. |
| 2 | `pyproject.toml` → `[tool.pytest.ini_options] testpaths = ["tests"]` | Even a bare `pytest` collects only `tests/`. `governance/tests/` is excluded **by configuration**. |
| 3 | `governance/conftest.py` registers the `decision` / `test_id` markers | Registration applies to the `governance/` subtree only. Marks placed on production tests in `tests/` are unregistered — warnings now, errors under `--strict-markers`. |
| 4 | `.github/workflows/ci.yml` | No `pytest` step, and no install of `pytest` or `pyyaml`. |

Verified directly: `python3 -m unittest discover -s governance/tests` errors, because the
governance tests are pytest-based (`request.session.items`, `iter_markers`) and unittest
cannot execute them at all.

**Consequence.** Commit `governance/` today and make CI a required check, and `TEST-G-001` is
committed but never executed. The test whose entire purpose is to prove that governed
decisions are bound to running code would itself be unbound and unrun — the same failure that
produced this remediation, reproduced one level up, inside the mechanism built to prevent it.

That is not an ironic aside. It is the specific reason this patch is blocking: a governance
suite that does not run is worse than none, because it reads as coverage.

## Required patch

**1. `pyproject.toml`** — collect both trees and register the markers centrally:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests", "governance/tests"]
markers = [
  "decision(id): governed decision this test enforces",
  "test_id(id): stable Atlas test identifier",
]
```

Central registration replaces `governance/conftest.py`; delete that file so the markers are
not defined in two places.

**2. `.github/workflows/ci.yml`** — add a step before `Static production build`:

```yaml
      - name: Governance suite
        run: |
          python -m pip install --quiet pytest pyyaml
          python -m pytest -q
```

**3. Branch protection** — mark the `test` job required on `main`. This is a GitHub setting,
not a repository file, and it is the load-bearing half of Codex's condition. Everything above
is inert without it.

## One detail that is easy to get wrong

`TEST-G-001` must run **in the same pytest session** as the tests it audits. It reads
`request.session.items` to find decision markers; the markers live on the production tests in
`tests/`. Running `pytest governance/tests` on its own collects no production tests, finds no
markers, and reports **every active decision as unenforced**.

That failure at least announces itself. The dangerous inversion is a future refactor that
makes the assertion vacuous instead — passing because it found nothing to check. Add to
`TEST-G-001` a guard asserting the session collected a non-zero number of decision markers,
so "nothing to check" fails rather than passes.

`testpaths = ["tests", "governance/tests"]` satisfies the same-session requirement for a bare
`pytest` invocation. Do not split it into two CI steps.

## Sequencing note

This patch lands **with** the governance scaffolding in step 1, not after it. A commit that
adds `governance/` without it produces a green CI run that proves nothing, and green runs are
very hard to revisit later.
