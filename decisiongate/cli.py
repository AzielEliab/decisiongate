"""Command-line interface for DecisionGATE.

    decisiongate ui   # 127.0.0.1:8791
    decisiongate version
    decisiongate check --statement "..." --evidence "..." --impact-pos "..."
                       --impact-neg "..." --values "..." --accountable "Name"
    decisiongate wrap --statement "..." -- -- CMD

Pre-execution filter. Not predictive, advisory, or prescriptive.
``wrap`` runs CMD only if all five gates PASS. Subprocess is the
user-supplied argv after ``--`` (no shell).
Forks always allowed.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from decisiongate import __version__
from decisiongate.engine import DecisionGATE
from decisiongate.gates import PASS
from decisiongate.proposal import Proposal, _as_list


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decisiongate",
        description=(
            "DecisionGATE — lightweight ethical pre-execution filter "
            "(Aziel Eliab, 2026). Not predictive, advisory, or prescriptive. "
            "Freedom without clarity is chaos. Clarity without force is wisdom. "
            "Local UI: `decisiongate ui` at http://127.0.0.1:8791."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_check = sub.add_parser(
        "check",
        help="Run the five gates on one proposal. Stops at the first failure.",
    )
    p_check.add_argument("--statement", default="", help="Concrete proposal statement.")
    p_check.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Fact/datum/observation. Repeatable; also accepts one-per-line.",
    )
    p_check.add_argument(
        "--impact-pos",
        action="append",
        default=[],
        dest="impact_pos",
        help="Positive impact. Repeatable.",
    )
    p_check.add_argument(
        "--impact-neg",
        action="append",
        default=[],
        dest="impact_neg",
        help="Negative impact. Repeatable.",
    )
    p_check.add_argument(
        "--values",
        action="append",
        default=[],
        help="Stated value. Repeatable.",
    )
    p_check.add_argument(
        "--commitments",
        action="append",
        default=[],
        help="Prior commitment. Repeatable.",
    )
    p_check.add_argument(
        "--constraints",
        action="append",
        default=[],
        help="Hard constraint. Repeatable.",
    )
    p_check.add_argument(
        "--accountable",
        default="",
        help="Named accountable owner.",
    )
    p_check.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full report (lineage, final_state, blocked_at) as JSON.",
    )

    p_ui = sub.add_parser(
        "ui",
        help="Serve the local filter UI on 127.0.0.1:8791.",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8791, help="Port (default 8791).")

    p_wrap = sub.add_parser(
        "wrap",
        help="Run CMD only if all five gates PASS. Put the command after -- .",
    )
    p_wrap.add_argument("--statement", default="", help="Concrete proposal statement.")
    p_wrap.add_argument("--evidence", action="append", default=[], help="Fact. Repeatable.")
    p_wrap.add_argument("--impact-pos", action="append", default=[], dest="impact_pos", help="Positive impact.")
    p_wrap.add_argument("--impact-neg", action="append", default=[], dest="impact_neg", help="Negative impact.")
    p_wrap.add_argument("--values", action="append", default=[], help="Stated value.")
    p_wrap.add_argument("--commitments", action="append", default=[], help="Prior commitment.")
    p_wrap.add_argument("--constraints", action="append", default=[], help="Hard constraint.")
    p_wrap.add_argument("--accountable", default="", help="Named accountable owner.")
    p_wrap.add_argument("--json", action="store_true", dest="as_json", help="Print the report as JSON.")


    p_doc = sub.add_parser("doctor", help="Self-check. No network, no telemetry.")
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print doctor results as JSON.")

    p_imp = sub.add_parser("import", help="Import a JSON document.")
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    p_exp.add_argument("path")

    return parser


def _flatten(values: list[str]) -> list[str]:
    out: list[str] = []
    for item in values:
        out.extend(_as_list(item))
    return out


def _proposal_from_ns(args: argparse.Namespace) -> Proposal:
    return Proposal(
        statement=args.statement,
        evidence=_flatten(args.evidence),
        impacts_positive=_flatten(args.impact_pos),
        impacts_negative=_flatten(args.impact_neg),
        values=_flatten(args.values),
        commitments=_flatten(args.commitments),
        constraints=_flatten(args.constraints),
        accountable_person=args.accountable,
    )


def _print_report(report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    for gate in report.lineage:
        print(f"{gate.name}: {gate.state}")
        if gate.feedback:
            print(f"  {gate.feedback}")
    print(f"final: {report.final_state}")
    if report.blocked_at:
        print(f"blocked_at: {report.blocked_at}")


def _cmd_wrap(gate_argv: list[str], cmd: list[str]) -> int:
    import subprocess

    parser = _build_parser()
    args = parser.parse_args(["wrap", *gate_argv])
    if not cmd:
        print("error: wrap requires `-- CMD` (the command after --)", file=sys.stderr)
        return 2
    report = DecisionGATE().run(_proposal_from_ns(args))
    _print_report(report, args.as_json)
    if report.final_state != PASS:
        print("wrap: refused (not all five gates PASS); command not run", file=sys.stderr)
        return 1
    # Subprocess only the user-supplied argv after --. Never shell=True.
    proc = subprocess.run(cmd)
    return int(proc.returncode)


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(argv) if argv is not None else sys.argv[1:]
    if raw and raw[0] == "wrap":
        rest = raw[1:]
        if "--" in rest:
            i = rest.index("--")
            return _cmd_wrap(rest[:i], rest[i + 1 :])
        return _cmd_wrap(rest, [])

    parser = _build_parser()
    args = parser.parse_args(raw)

    if args.cmd == "version":
        print(f"decisiongate {__version__}")
        return 0

    if args.cmd == "check":
        report = DecisionGATE().run(_proposal_from_ns(args))
        _print_report(report, args.as_json)
        return 0 if report.final_state == PASS else 1

    if args.cmd == "ui":
        from decisiongate.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0


    if args.cmd == "doctor":
        from decisiongate.doctor import run_doctor

        return run_doctor(as_json=getattr(args, "as_json", False))

    if args.cmd == "import":
        from decisiongate.jsonio import import_json

        rec = import_json(args.path)
        sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return 0

    if args.cmd == "export":
        from decisiongate.jsonio import export_json

        rec = export_json(args.path)
        sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return 0

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
