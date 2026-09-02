"""Self-check for DecisionGATE. No network, no telemetry.

    decisiongate doctor
    decisiongate verify

Prints plain sentences a kid can read. Not advice.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

from decisiongate import LIMITATION, __version__

AUTHOR = "Aziel Eliab"
Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__:
        return _ok("version", str(__version__))
    return _fail("version", "missing")


def _check_identity() -> Check:
    try:
        mod = __import__(__name__.split(".")[0])
        author = str(getattr(mod, "__author__", AUTHOR))
    except Exception as exc:  # noqa: BLE001
        return _fail("identity", str(exc))
    blob = author + " " + AUTHOR
    forbidden = ("Col" + "lin H" + "orton", "Ja" + "ck Al" + "tman", "GodLock" + ".AZ", "Reve" + "aler")
    if any(x in blob for x in forbidden):
        return _fail("identity", "forbidden identity label")
    if "Aziel Eliab" not in blob:
        return _fail("identity", author)
    return _ok("identity", AUTHOR)


def _check_json_roundtrip() -> Check:
    from decisiongate.jsonio import export_json, import_json

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.json"
        out = Path(tmp) / "out.json"
        src.write_text(
            json.dumps({"product": "decisiongate", "author": AUTHOR, "ok": True}, indent=2),
            encoding="utf-8",
        )
        rec = import_json(src, store_dir=tmp)
        if not rec.get("ok"):
            return _fail("import", str(rec))
        rec2 = export_json(out, store_dir=tmp)
        if not rec2.get("ok") or not out.exists():
            return _fail("export", str(rec2))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("author") != AUTHOR:
            return _fail("export author", str(doc.get("author")))
        return _ok("json import/export", "roundtrip")


def _check_loopback() -> Check:
    from decisiongate.ui import LOOPBACK, make_server

    try:
        make_server("0.0.0.0", 9)
    except ValueError as exc:
        if "loopback" in str(exc).lower() and "127.0.0.1" in LOOPBACK:
            return _ok("loopback", "rejects 0.0.0.0")
        return _fail("loopback", str(exc))
    return _fail("loopback", "accepted 0.0.0.0")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_json_roundtrip,
    _check_loopback,
)


def _plain_line(name: str, ok: bool, detail: str) -> str:
    if name == "version":
        return (
            f"The program is version {detail}."
            if ok
            else f"The program version is missing ({detail})."
        )
    if name == "identity":
        return (
            "The author name is Aziel Eliab."
            if ok
            else f"The author name is wrong ({detail})."
        )
    if name == "json import/export":
        return (
            "Saving a file and loading it back works."
            if ok
            else f"Saving a file and loading it back failed ({detail})."
        )
    if name == "loopback":
        return (
            "The screen only opens on this computer."
            if ok
            else f"The screen bind check failed ({detail})."
        )
    extra = f" ({detail})" if detail else ""
    return f"{name}: {'ok' if ok else 'not ok'}{extra}."


def collect_doctor() -> dict:
    results = []
    plain = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        plain.append(_plain_line(name, ok, detail))
        if not ok:
            failed += 1
    if failed == 0:
        summary = "Doctor says: the checks passed. This is not advice. It is a check that the filter is installed."
    else:
        summary = "Doctor says: something is not working. This is not advice."
    plain.append(summary)
    return {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "plain": plain,
        "summary": summary,
        "version": __version__,
        "author": AUTHOR,
        "limitation": LIMITATION,
        "network": False,
        "telemetry": False,
    }


def run_doctor(*, as_json: bool = False) -> int:
    payload = collect_doctor()
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        for line in payload["plain"]:
            print(line)
        print("limitation:", LIMITATION)
        print("doctor", "passed" if payload["ok"] else "failed")
    return 0 if payload["ok"] else 1
