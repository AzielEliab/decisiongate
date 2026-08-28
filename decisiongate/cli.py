"""Command-line interface for DecisionGATE.

    decisiongate version
    decisiongate check --statement "..." --evidence "..." --impact-pos "..."
                       --impact-neg "..." --values "..." --accountable "Name"
    decisiongate ui   # 127.0.0.1:8791

Pre-execution filter. Not predictive, advisory, or prescriptive.
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
            "Freedom without clarity is chaos. Clarity without force is wisdom."
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

    return parser


def _flatten(values: list[str]) -> list[str]:
    out: list[str] = []
    for item in values:
        out.extend(_as_list(item))
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"decisiongate {__version__}")
        return 0

    if args.cmd == "check":
        proposal = Proposal(
            statement=args.statement,
            evidence=_flatten(args.evidence),
            impacts_positive=_flatten(args.impact_pos),
            impacts_negative=_flatten(args.impact_neg),
            values=_flatten(args.values),
            commitments=_flatten(args.commitments),
            constraints=_flatten(args.constraints),
            accountable_person=args.accountable,
        )
        report = DecisionGATE().run(proposal)
        if args.as_json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        else:
            for gate in report.lineage:
                print(f"{gate.name}: {gate.state}")
                if gate.feedback:
                    print(f"  {gate.feedback}")
            print(f"final: {report.final_state}")
            if report.blocked_at:
                print(f"blocked_at: {report.blocked_at}")
        return 0 if report.final_state == PASS else 1

    if args.cmd == "ui":
        from decisiongate.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
