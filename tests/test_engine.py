"""Engine: sequential stop, lineage, blocked_at, human override."""

from __future__ import annotations

from decisiongate.engine import DecisionGATE
from decisiongate.gates import BLOCK, PASS, REVISE
from tests.helpers import complete_proposal


def test_run_stops_at_first_failure_empty_statement() -> None:
    report = DecisionGATE().run(complete_proposal(statement=""))
    assert len(report.lineage) == 1
    assert report.lineage[0].name == "Definition"
    assert report.lineage[0].state in {REVISE, BLOCK}
    assert report.final_state == report.lineage[0].state
    if report.final_state == BLOCK:
        assert report.blocked_at == "Definition"
    else:
        assert report.blocked_at is None


def test_run_stops_at_evidence() -> None:
    report = DecisionGATE().run(complete_proposal(evidence=[]))
    assert [g.name for g in report.lineage] == ["Definition", "Evidence"]
    assert report.lineage[0].state == PASS
    assert report.lineage[1].state == REVISE
    assert report.final_state == REVISE
    assert report.blocked_at is None


def test_run_stops_at_responsibility_block() -> None:
    report = DecisionGATE().run(complete_proposal(accountable_person=""))
    assert [g.name for g in report.lineage] == [
        "Definition",
        "Evidence",
        "Impact",
        "Integrity",
        "Responsibility",
    ]
    assert report.lineage[-1].state == BLOCK
    assert report.final_state == BLOCK
    assert report.blocked_at == "Responsibility"


def test_override_to_revise_recorded_in_lineage() -> None:
    report = DecisionGATE().run(
        complete_proposal(),
        overrides={"Definition": {"state": "REVISE", "note": "I want a tighter verb."}},
    )
    assert len(report.lineage) == 1
    gate = report.lineage[0]
    assert gate.state == REVISE
    assert gate.overridden is True
    assert gate.automatic_state == PASS
    assert "tighter verb" in gate.feedback
    assert report.final_state == REVISE
    payload = report.to_dict()
    assert payload["lineage"][0]["overridden"] is True
    assert payload["lineage"][0]["override_note"] == "I want a tighter verb."
