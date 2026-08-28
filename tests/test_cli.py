"""CLI: version, check, JSON lineage."""

from __future__ import annotations

import json

from decisiongate import __version__
from decisiongate.cli import main
from tests.helpers import COMPLETE_STATEMENT


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"decisiongate {__version__}"


def test_cli_check_complete_pass(capsys) -> None:
    code = main(
        [
            "check",
            "--statement",
            COMPLETE_STATEMENT,
            "--evidence",
            "Whitepaper dated July 2026 names five sequential gates.",
            "--impact-pos",
            "Authors get a named scrutiny path before acting.",
            "--impact-neg",
            "Vague drafts take longer because they must be rewritten.",
            "--values",
            "Clarity without force",
            "--accountable",
            "Aziel Eliab",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "Definition: PASS" in out
    assert "Evidence: PASS" in out
    assert "Impact: PASS" in out
    assert "Integrity: PASS" in out
    assert "Responsibility: PASS" in out
    assert "final: PASS" in out


def test_cli_check_no_evidence_nonzero(capsys) -> None:
    code = main(
        [
            "check",
            "--statement",
            COMPLETE_STATEMENT,
            "--impact-pos",
            "A benefit.",
            "--impact-neg",
            "A cost.",
            "--values",
            "clarity",
            "--accountable",
            "Aziel Eliab",
        ]
    )
    out = capsys.readouterr().out
    assert code == 1
    assert "Evidence: REVISE" in out
    assert "final: REVISE" in out


def test_cli_check_json_lineage(capsys) -> None:
    code = main(
        [
            "check",
            "--json",
            "--statement",
            COMPLETE_STATEMENT,
            "--evidence",
            "A fact.",
            "--impact-pos",
            "A benefit.",
            "--impact-neg",
            "A cost.",
            "--values",
            "clarity",
            "--accountable",
            "Aziel Eliab",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["final_state"] == "PASS"
    assert [g["name"] for g in payload["lineage"]] == [
        "Definition",
        "Evidence",
        "Impact",
        "Integrity",
        "Responsibility",
    ]
