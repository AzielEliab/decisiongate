"""File import AND export (not export-only)."""

from __future__ import annotations

import json
from pathlib import Path

from decisiongate.cli import main
from decisiongate.jsonio import export_json, import_json


def test_import_and_export_roundtrip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "in.json"
    src.write_text(
        json.dumps({"statement": "hello from import", "author": "Aziel Eliab"}),
        encoding="utf-8",
    )
    rec = import_json(src)
    assert rec["ok"] is True
    assert rec["author"] == "Aziel Eliab"
    out = tmp_path / "out.json"
    rec2 = export_json(out)
    assert rec2["ok"] is True
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["author"] == "Aziel Eliab"
    assert doc["product"] == "DecisionGATE"
    assert doc["payload"]["statement"] == "hello from import"


def test_cli_import_export(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "a.json"
    src.write_text(json.dumps({"ok": True, "n": 1}), encoding="utf-8")
    assert main(["import", str(src)]) == 0
    imported = json.loads(capsys.readouterr().out)
    assert imported["ok"] is True
    dst = tmp_path / "b.json"
    assert main(["export", str(dst)]) == 0
    exported = json.loads(capsys.readouterr().out)
    assert exported["ok"] is True
    assert dst.is_file()
    assert "Aziel Eliab" in dst.read_text(encoding="utf-8")
