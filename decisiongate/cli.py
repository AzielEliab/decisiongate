"""Command-line interface for DecisionGATE.

    decisiongate
    decisiongate ui
    decisiongate check --statement "..." --evidence "..." --impact-pos "..."
                       --impact-neg "..." --values "..." --accountable "Name"
    decisiongate doctor
    decisiongate wrap --statement "..." -- -- CMD
    decisiongate import FILE.json
    decisiongate export FILE.json

``wrap`` runs CMD only if all five gates PASS. Subprocess is the
user-supplied argv after ``--`` (no shell).
File import and export both exist. ``--json`` keeps the machine record.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Sequence

from decisiongate import __author__, __version__
from decisiongate.engine import DecisionGATE
from decisiongate.gates import PASS, REVISE
from decisiongate.proposal import Proposal, _as_list

class DecisionGateParser(argparse.ArgumentParser):
    """Plain misuse messages: reason, then one next step."""

    def error(self, message: str) -> None:
        prog = self._hint_prog()
        choice = re.search(r"invalid choice: '([^']*)'", message)
        if choice:
            bad = choice.group(1)
            self.exit(
                2,
                f'Unknown command "{bad}". Try: decisiongate ui   or   decisiongate --help\n',
            )
        if message.startswith("unrecognized arguments:"):
            junk = message.split(":", 1)[1].strip().split()
            shown = junk[0] if junk else "that option"
            self.exit(2, f'Unknown option "{shown}". Try: {prog} --help\n')
        if "the following arguments are required" in message:
            if re.search(r"\b(cmd|command)\b", message):
                self.exit(
                    2,
                    "Try: decisiongate ui   or   decisiongate --help\n",
                )
            if "path" in message:
                self.exit(2, f"{prog} needs a file path. Try: {prog} --help\n")
            self.exit(2, f"This command needs more information. Try: {prog} --help\n")
        self.exit(2, f"{message}. Try: {prog} --help\n")

    def _hint_prog(self) -> str:
        argv = getattr(self, "_dg_argv", None) or []
        known = {
            "ui",
            "check",
            "doctor",
            "version",
            "wrap",
            "verify",
            "import",
            "export",
        }
        if argv and argv[0] in known:
            return f"decisiongate {argv[0]}"
        return self.prog


def _build_parser() -> DecisionGateParser:
    parser = DecisionGateParser(
        prog="decisiongate",
        description=(
            "Check a plan through five gates before you act.\n"
            f"Author: {__author__}."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  decisiongate\n"
            "  decisiongate ui\n"
            "  decisiongate doctor\n"
            "  decisiongate check --help\n"
            "\n"
            "Open the local screen at http://127.0.0.1:8791/ with `decisiongate ui`.\n"
            "Add --json on a command when a program should read the result."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the welcome as JSON. On a command, put --json after the command name.",
    )
    sub = parser.add_subparsers(dest="cmd", required=False, metavar="command")

    ui = sub.add_parser("ui", help="Open the local screen at http://127.0.0.1:8791")
    ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    ui.add_argument("--port", type=int, default=8791, help="Port (default 8791).")

    check = sub.add_parser("check", help="Run the five gates on one plan")
    _add_plan_args(check)

    doctor = sub.add_parser(
        "doctor",
        aliases=["verify"],
        help="Check that this install works (verify is the same command)",
    )
    doctor.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print doctor results as JSON.",
    )

    sub.add_parser("version", help="Print the version")

    wrap = sub.add_parser(
        "wrap",
        help="More: run a command only if every gate passes",
    )
    _add_plan_args(wrap)

    imp = sub.add_parser("import", help="More: load a JSON file")
    imp.add_argument("path", help="Path to a .json file to load.")
    imp.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the import record as JSON.",
    )

    exp = sub.add_parser("export", help="More: save a JSON file")
    exp.add_argument("path", help="Path to write a .json file.")
    exp.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the export record as JSON.",
    )
    return parser


def _add_plan_args(target: argparse.ArgumentParser) -> None:
    target.add_argument("--statement", default="", help="Concrete plan, in plain words.")
    target.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Fact, datum, or observation. Repeatable.",
    )
    target.add_argument(
        "--impact-pos",
        action="append",
        default=[],
        dest="impact_pos",
        help="Who is helped, or what improves. Repeatable.",
    )
    target.add_argument(
        "--impact-neg",
        action="append",
        default=[],
        dest="impact_neg",
        help="Who is burdened, or what it costs. Repeatable.",
    )
    target.add_argument(
        "--values",
        action="append",
        default=[],
        help="A value you already stated. Repeatable.",
    )
    target.add_argument(
        "--commitments",
        action="append",
        default=[],
        help="A prior commitment. Repeatable.",
    )
    target.add_argument(
        "--constraints",
        action="append",
        default=[],
        help="A hard constraint. Repeatable.",
    )
    target.add_argument("--accountable", default="", help="Named accountable owner.")
    target.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full report (lineage, final_state, blocked_at) as JSON.",
    )


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


def _closing_line(report) -> str:
    if report.final_state == PASS:
        return "All five checks passed. The plan was clear enough to inspect."
    stopped = report.lineage[-1].name if report.lineage else "a gate"
    if report.final_state == REVISE:
        return (
            f"Revise the plan. {stopped} needs a more specific answer. "
            "Try: decisiongate check --help"
        )
    where = report.blocked_at or stopped
    return f"Stopped at {where}. Change the plan, then run the check again."


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
    print(_closing_line(report))


def _print_welcome(as_json: bool) -> None:
    if as_json:
        print(
            json.dumps(
                {
                    "product": "decisiongate",
                    "version": __version__,
                    "author": __author__,
                    "summary": "DecisionGATE checks a plan through five gates before you act.",
                    "ui": "http://127.0.0.1:8791/",
                    "next": [
                        "decisiongate ui",
                        "decisiongate check --help",
                        "decisiongate doctor",
                    ],
                },
                indent=2,
            )
        )
        return
    print("DecisionGATE checks a plan through five gates before you act.")
    print()
    print("Open the local screen:")
    print("  decisiongate ui")
    print()
    print("Other next steps:")
    print("  decisiongate check --help")
    print("  decisiongate doctor")
    print()
    print(f"Author: {__author__}")


def _parse(parser: DecisionGateParser, argv: list[str]) -> argparse.Namespace | int:
    parser._dg_argv = list(argv)  # noqa: SLF001
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else int(code)


def _cmd_wrap(gate_argv: list[str], cmd: list[str]) -> int:
    import subprocess

    parser = _build_parser()
    parsed = _parse(parser, ["wrap", *gate_argv])
    if isinstance(parsed, int):
        return parsed
    if not cmd:
        print(
            "wrap needs a command after --. Try: decisiongate wrap --help",
            file=sys.stderr,
        )
        return 2
    report = DecisionGATE().run(_proposal_from_ns(parsed))
    _print_report(report, parsed.as_json)
    if report.final_state != PASS:
        print(
            "wrap: refused (not all five gates PASS); command not run. "
            "Try: decisiongate check --help",
            file=sys.stderr,
        )
        return 1
    # Subprocess only the user-supplied argv after --. Never shell=True.
    proc = subprocess.run(cmd)
    return int(proc.returncode)


def _cmd_import(path: str, as_json: bool) -> int:
    from decisiongate.jsonio import import_json

    try:
        rec = import_json(path)
    except FileNotFoundError:
        print(
            f'No file at "{path}". Try: decisiongate import FILE.json',
            file=sys.stderr,
        )
        return 2
    except json.JSONDecodeError:
        print(
            "That file is not JSON. Try: decisiongate import FILE.json",
            file=sys.stderr,
        )
        return 2
    except ValueError as exc:
        print(f"{exc}. Try: decisiongate import FILE.json", file=sys.stderr)
        return 2
    except OSError as exc:
        print(
            f"Could not save the import ({exc.strerror or exc}). "
            "Try: decisiongate import FILE.json",
            file=sys.stderr,
        )
        return 2
    if as_json:
        sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return 0
    print(f"Imported {rec.get('imported', path)}.")
    print("Saved on this computer. Next: decisiongate export FILE.json")
    return 0


def _cmd_export(path: str, as_json: bool) -> int:
    from decisiongate.jsonio import export_json

    try:
        rec = export_json(path)
    except OSError as exc:
        print(
            f"Could not write that file ({exc.strerror or exc}). "
            "Try: decisiongate export FILE.json",
            file=sys.stderr,
        )
        return 2
    if as_json:
        sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return 0
    print(f"Exported {rec.get('exported', path)}.")
    print("Next: decisiongate import FILE.json")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(argv) if argv is not None else sys.argv[1:]
    if raw and raw[0] == "wrap":
        rest = raw[1:]
        if "--" in rest:
            i = rest.index("--")
            return _cmd_wrap(rest[:i], rest[i + 1 :])
        return _cmd_wrap(rest, [])

    parser = _build_parser()
    parsed = _parse(parser, raw)
    if isinstance(parsed, int):
        return parsed
    args = parsed

    if args.cmd is None:
        _print_welcome(bool(args.as_json))
        return 0

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
            print(f"{exc}. Try: decisiongate ui", file=sys.stderr)
            return 2
        except OSError as exc:
            print(
                f"The local screen could not start ({exc.strerror or exc}). "
                "Try: decisiongate ui --port 8792",
                file=sys.stderr,
            )
            return 2
        return 0

    if args.cmd in {"doctor", "verify"}:
        from decisiongate.doctor import run_doctor

        return run_doctor(as_json=getattr(args, "as_json", False))

    if args.cmd == "import":
        return _cmd_import(args.path, bool(getattr(args, "as_json", False)))

    if args.cmd == "export":
        return _cmd_export(args.path, bool(getattr(args, "as_json", False)))

    print(
        f'Unknown command "{args.cmd}". Try: decisiongate ui   or   decisiongate --help',
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
