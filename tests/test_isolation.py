"""This tree is DecisionGATE only. Worker undeployed. Not merged elsewhere."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_worker_kv_is_placeholder() -> None:
    toml = (ROOT / "workers" / "download-tracker" / "wrangler.toml").read_text()
    assert 'name = "decisiongate-download-tracker"' in toml
    assert "REPLACE_ME" in toml
    assert "account_id = \"ac575a9b822bea2bed97d0ab73aed238\"" in toml
    src = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text()
    assert 'const PROJECT = "decisiongate"' in src
    assert "decisiongate-0.1.0.tar.gz" in src
    assert "Freedom without clarity is chaos" in src
    assert "Isolated counter" in src
    assert "forgereceipts" not in src.lower()
    assert "zionpattern" not in src.lower().replace("-", "").replace("_", "").replace(" ", "")


def test_not_inside_sibling_products() -> None:
    text = str(ROOT)
    assert text.endswith("decisiongate") or "/decisiongate" in text
    assert "forgereceipts" not in text
    assert "zion-pattern" not in text
    assert (ROOT / "decisiongate" / "engine.py").is_file()
    assert not (ROOT / "forgereceipts").exists()
