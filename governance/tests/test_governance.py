"""TEST-G-001 — governed decisions must be enforced by tests that exist.

This is the test that would have caught the Phase 1.1 universe-provider defect at PR
open, rather than three handoffs downstream at deployment verification. Its purpose is
not to check economics; it is to check that every economic decision on the books is
bound to executable code.

Two directions, both required:

  forward   every active decision with a non-empty enforced_by list has at least one
            collected test carrying that decision marker
  reverse   every decision marker appearing in the suite resolves to a decision file
            whose status is active

The reverse direction matters as much as the forward one: a test marked @decision("D-014")
when no D-014 exists means someone invented a requirement, and a test still marked with a
superseded decision means someone kept enforcing a rule that was withdrawn.
"""

import pathlib
import pytest
import yaml

DECISIONS_DIR = pathlib.Path(__file__).resolve().parents[1] / "decisions"


def decision_marker(decision_id):
    """Attach a governed decision to a test. Prose comments do not count."""
    return pytest.mark.decision(decision_id)


def load_decisions():
    out = {}
    for path in sorted(DECISIONS_DIR.glob("D-*.yaml")):
        record = yaml.safe_load(path.read_text())
        assert record["id"] == path.stem, f"{path}: id does not match filename"
        assert record["id"] not in out, f"{path}: duplicate decision id"
        assert record["status"] in {
            "active",
            "adopted_pending_implementation",
            "superseded",
        }, f"{path}: unsupported decision status {record['status']!r}"
        out[record["id"]] = record
    return out


def collected_decision_markers(session_items):
    seen = {}
    for item in session_items:
        for mark in item.iter_markers(name="decision"):
            seen.setdefault(mark.args[0], []).append(item.nodeid)
    return seen


def test_g_001_every_active_decision_is_enforced(request):
    decisions = load_decisions()
    assert decisions, "no decision records found — governance directory is empty"
    markers = collected_decision_markers(request.session.items)
    marker_count = sum(len(nodeids) for nodeids in markers.values())
    assert marker_count > 0, (
        "no decision markers were collected; governance must run in the same "
        "pytest session as production tests"
    )

    unenforced = [
        did
        for did, rec in decisions.items()
        if rec["status"] == "active" and rec.get("enforced_by") and did not in markers
    ]
    assert not unenforced, (
        "active decisions with no enforcing test in the suite: "
        + ", ".join(sorted(unenforced))
        + ". A decision that no test binds to is not in force."
    )

    dangling = [did for did in markers if did not in decisions]
    assert not dangling, (
        "tests reference decisions that do not exist: " + ", ".join(sorted(dangling))
    )

    non_active = [
        did
        for did in markers
        if did in decisions and decisions[did]["status"] != "active"
    ]
    assert not non_active, (
        "tests reference decisions that are not active: "
        + ", ".join(sorted(non_active))
    )


def test_g_002_declared_tests_exist(request):
    """Each decision's enforced_by names test IDs; those IDs must appear in the suite."""
    decisions = load_decisions()
    suite_ids = set()
    for item in request.session.items:
        for mark in item.iter_markers(name="test_id"):
            suite_ids.add(mark.args[0])

    missing = {}
    for did, rec in decisions.items():
        if rec["status"] != "active":
            continue
        absent = [t for t in rec.get("enforced_by") or [] if t not in suite_ids]
        if absent:
            missing[did] = absent
    assert not missing, f"decisions name tests that do not exist in the suite: {missing}"
