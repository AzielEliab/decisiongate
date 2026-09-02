"""Local UI: loopback only, GET / contains DecisionGATE, check API."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from decisiongate.ui import LOOPBACK, make_server
from tests.helpers import COMPLETE_STATEMENT


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def test_ui_get_root_200_contains_decisiongate() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
        assert "DecisionGATE" in html
        assert "Freedom without clarity is chaos" in html
        assert "Import file" in html
        assert "Export file" in html
        assert "Verify" in html
        assert "THIS IS" in html
        assert "THIS IS NOT" in html
        assert "Simple" in html
        assert "cdnjs" not in html.lower()
        assert "unpkg" not in html.lower()
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/verify", timeout=3) as resp:
            doctor = json.loads(resp.read().decode("utf-8"))
        assert doctor["ok"] is True
        assert doctor["author"] == "Aziel Eliab"
        assert any("Aziel Eliab" in x for x in doctor["plain"])
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/style.css", timeout=3) as resp:
            css = resp.read().decode("utf-8")
        assert "PASS" in css or "--pass" in css
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/check",
            data=json.dumps(
                {
                    "statement": COMPLETE_STATEMENT,
                    "evidence": ["A documented observation."],
                    "impacts_positive": ["A named benefit."],
                    "impacts_negative": ["A named cost."],
                    "values": ["clarity"],
                    "accountable_person": "Aziel Eliab",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["final_state"] == "PASS"
        assert len(payload["lineage"]) == 5
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_ui_api_empty_statement_stops() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/check",
            data=json.dumps({"statement": ""}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert len(payload["lineage"]) == 1
        assert payload["lineage"][0]["name"] == "Definition"
    finally:
        httpd.shutdown()
        httpd.server_close()
