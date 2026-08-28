#!/usr/bin/env python3
"""Run one proposal through DecisionGATE. Filter, do not advise."""

from __future__ import annotations

from decisiongate import DecisionGATE, Proposal


def main() -> None:
    proposal = Proposal(
        statement=(
            "Release DecisionGATE 0.1.0 as a standalone Python package "
            "with Apache-2.0 licensing on GitHub this month."
        ),
        evidence=["Whitepaper dated July 2026 names five sequential gates."],
        impacts_positive=["Authors get a named scrutiny path before acting."],
        impacts_negative=["Vague drafts take longer because they must be rewritten."],
        values=["Clarity without force", "Named responsibility"],
        commitments=["Apache-2.0"],
        constraints=["Do not bind the UI on 0.0.0.0"],
        accountable_person="Aziel Eliab",
    )
    report = DecisionGATE().run(proposal)
    print(f"final: {report.final_state}")
    for gate in report.lineage:
        print(f"{gate.name}: {gate.state}")
        print(f"  {gate.feedback}")


if __name__ == "__main__":
    main()
