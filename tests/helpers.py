"""Shared proposal builders for tests."""

from __future__ import annotations

from decisiongate.proposal import Proposal

COMPLETE_STATEMENT = (
    "Release DecisionGATE 0.1.0 as a standalone Python package "
    "with Apache-2.0 licensing on GitHub this month."
)


def complete_proposal(**changes) -> Proposal:
    data = dict(
        statement=COMPLETE_STATEMENT,
        evidence=["Whitepaper dated July 2026 names five sequential gates."],
        impacts_positive=["Authors get a named scrutiny path before acting."],
        impacts_negative=["Vague drafts take longer because they must be rewritten."],
        values=["Clarity without force", "Named responsibility"],
        commitments=["Apache-2.0", "Forks welcome"],
        constraints=["Do not bind the UI on 0.0.0.0"],
        accountable_person="Aziel Eliab",
    )
    data.update(changes)
    return Proposal.from_dict(data)
