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


def test_help_lists_ui_and_version() -> None:
    from decisiongate.cli import _build_parser

    text = _build_parser().format_help()
    assert "ui" in text
    assert "version" in text
    assert "wrap" in text
    assert "doctor" in text
    assert "import" in text
    assert "export" in text
    assert "127.0.0.1:8791" in text or "decisiongate ui" in text


def test_wrap_failing_statement_does_not_run_dummy(tmp_path, capsys) -> None:
    import sys

    marker = tmp_path / "ran.txt"
    dummy = [sys.executable, "-c", f"open({str(marker)!r}, 'w').write('ran')"]
    code = main(["wrap", "--statement", "maybe stuff", "--", *dummy])
    captured = capsys.readouterr()
    assert code != 0
    assert not marker.exists()
    blob = captured.out + captured.err
    assert "refused" in blob.lower() or "REVISE" in blob or "BLOCK" in blob


def test_wrap_pass_runs_dummy(tmp_path, capsys) -> None:
    import sys

    marker = tmp_path / "ran.txt"
    dummy = [sys.executable, "-c", f"open({str(marker)!r}, 'w').write('ok')"]
    code = main(
        [
            "wrap",
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
            "--",
            *dummy,
        ]
    )
    capsys.readouterr()
    assert code == 0
    assert marker.read_text(encoding="utf-8") == "ok"


def test_wrap_missing_command_nonzero(capsys) -> None:
    code = main(
        [
            "wrap",
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
    err = capsys.readouterr().err
    assert code == 2
    assert "CMD" in err or "command" in err.lower()
