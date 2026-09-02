"""Doctor / verify: plain words, identity, import+export roundtrip."""

from __future__ import annotations

import json

from decisiongate.cli import main
from decisiongate.doctor import collect_doctor, run_doctor


def test_doctor_passes_json(capsys) -> None:
    assert run_doctor(as_json=True) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["author"] == "Aziel Eliab"
    assert payload["network"] is False
    assert payload["telemetry"] is False
    names = [c["name"] for c in payload["checks"]]
    assert "identity" in names
    assert "json import/export" in names
    assert "loopback" in names
    blob = " ".join(payload["plain"])
    assert "Aziel Eliab" in blob
    assert "not advice" in blob.lower()


def test_cli_verify_alias_plain(capsys) -> None:
    assert main(["verify"]) == 0
    out = capsys.readouterr().out
    assert "Aziel Eliab" in out
    assert "Saving a file and loading it back works" in out
    assert "doctor passed" in out


def test_collect_doctor_limitation() -> None:
    payload = collect_doctor()
    assert payload["ok"] is True
    assert "predictor" in payload["limitation"].lower() or "THIS IS NOT" in payload["limitation"]
