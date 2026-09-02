"""JSON file import and export for DecisionGATE. Author: Aziel Eliab.

Import a .json file. Export a .json file. Both exist. Not export-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from decisiongate import __version__

AUTHOR = "Aziel Eliab"
PRODUCT = "DecisionGATE"
STATE_NAME = ".decisiongate-state.json"


def _as_path(path: str | Path) -> Path:
    return Path(path)


def import_json(path: str | Path, *, store_dir: str | Path | None = None) -> dict[str, Any]:
    """Load a JSON object from a file and store it locally."""
    pth = _as_path(path)
    if not pth.is_file():
        raise FileNotFoundError("import file not found: " + str(pth))
    doc = json.loads(pth.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("JSON object required")
    base = _as_path(store_dir) if store_dir is not None else Path.cwd()
    dest = base / STATE_NAME
    dest.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "imported": str(pth),
        "stored": str(dest),
        "keys": sorted(str(k) for k in doc.keys()),
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
    }


def export_json(path: str | Path, *, store_dir: str | Path | None = None) -> dict[str, Any]:
    """Write a JSON file. Includes author Aziel Eliab. Pair of import, not export-only."""
    pth = _as_path(path)
    base = _as_path(store_dir) if store_dir is not None else Path.cwd()
    src = base / STATE_NAME
    payload: Any = {}
    if src.exists():
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    if not isinstance(payload, dict):
        payload = {"value": payload}
    doc = {
        "product": PRODUCT,
        "package": "decisiongate",
        "version": __version__,
        "author": AUTHOR,
        "payload": payload,
    }
    pth.parent.mkdir(parents=True, exist_ok=True)
    pth.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "exported": str(pth),
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
    }
