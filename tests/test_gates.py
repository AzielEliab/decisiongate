"""Gate heuristics: empty, vague, evidence, impact, integrity, responsibility."""

from __future__ import annotations

from decisiongate.engine import DecisionGATE
from decisiongate.gates import (
    BLOCK,
    PASS,
    REVISE,
    gate_definition,
    gate_evidence,
    gate_impact,
    gate_integrity,
    gate_responsibility,
)
from decisiongate.proposal import Proposal
from tests.helpers import COMPLETE_STATEMENT, complete_proposal


def test_empty_statement_revise_or_block() -> None:
    result = gate_definition(Proposal(statement=""))
    assert result.name == "Definition"
    assert result.state in {REVISE, BLOCK}
    assert "empty" in result.feedback.lower()


def test_short_statement_revise() -> None:
    result = gate_definition(Proposal(statement="Ship the thing now."))
    assert result.state == REVISE
    assert "12" in result.feedback


def test_hedge_only_statement_revise() -> None:
    # 12+ tokens but only hedges, no verb+object after stripping.
    statement = "maybe somehow stuff things maybe somehow stuff things maybe somehow stuff things"
    result = gate_definition(Proposal(statement=statement))
    assert result.state == REVISE
    assert "verb" in result.feedback.lower() or "hedge" in result.feedback.lower()


def test_complete_statement_definition_pass() -> None:
    result = gate_definition(Proposal(statement=COMPLETE_STATEMENT))
    assert result.state == PASS


def test_no_evidence_revise() -> None:
    result = gate_evidence(Proposal(statement=COMPLETE_STATEMENT, evidence=[]))
    assert result.state == REVISE
    assert "empty" in result.feedback.lower()


def test_missing_negative_impact_revise() -> None:
    result = gate_impact(
        Proposal(
            impacts_positive=["Authors get a named path."],
            impacts_negative=[],
        )
    )
    assert result.state == REVISE
    assert "negative" in result.feedback.lower()


def test_missing_positive_impact_revise() -> None:
    result = gate_impact(
        Proposal(
            impacts_positive=[],
            impacts_negative=["Rewrites take time."],
        )
    )
    assert result.state == REVISE
    assert "positive" in result.feedback.lower()


def test_empty_values_integrity_revise() -> None:
    result = gate_integrity(Proposal(values=[], constraints=[]))
    assert result.state == REVISE
    assert "values" in result.feedback.lower()


def test_constraint_contradiction_integrity_block() -> None:
    result = gate_integrity(
        Proposal(
            statement="Collect personal email addresses from every visitor to the site.",
            values=["privacy"],
            constraints=["Do not collect personal email addresses"],
        )
    )
    assert result.state == BLOCK
    assert "contradict" in result.feedback.lower()


def test_no_accountable_block() -> None:
    result = gate_responsibility(Proposal(accountable_person=""))
    assert result.state == BLOCK
    assert "blank" in result.feedback.lower() or "absent" in result.feedback.lower()


def test_named_accountable_pass() -> None:
    result = gate_responsibility(Proposal(accountable_person="Aziel Eliab"))
    assert result.state == PASS


def test_complete_proposal_pass_all_five() -> None:
    report = DecisionGATE().run(complete_proposal())
    assert [g.name for g in report.lineage] == [
        "Definition",
        "Evidence",
        "Impact",
        "Integrity",
        "Responsibility",
    ]
    assert all(g.state == PASS for g in report.lineage)
    assert report.final_state == PASS
    assert report.blocked_at is None
    assert len(report.lineage) == 5
