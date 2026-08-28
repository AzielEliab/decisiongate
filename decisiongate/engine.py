"""DecisionGATE engine: run five gates in order, stop at first failure.

Default path is automatic. A human may override a gate to REVISE with a
note; the override is recorded in lineage. Overrides do not skip a
failure — REVISE and BLOCK both stop the chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from decisiongate.gates import (
    BLOCK,
    GATE_FUNCS,
    GATE_ORDER,
    PASS,
    REVISE,
    GateResult,
)
from decisiongate.proposal import Proposal

VALID_OVERRIDE_STATES = frozenset({REVISE})


def _coerce_overrides(
    overrides: Mapping[str, Any] | None,
) -> dict[str, tuple[str, str]]:
    """Map gate name -> (REVISE, note). Unknown gates ignored."""
    out: dict[str, tuple[str, str]] = {}
    if not overrides:
        return out
    known = {n.lower(): n for n in GATE_ORDER}
    for key, raw in overrides.items():
        name = known.get(str(key).strip().lower())
        if not name:
            continue
        note = ""
        state = REVISE
        if isinstance(raw, str):
            note = raw.strip()
        elif isinstance(raw, Mapping):
            state_raw = str(raw.get("state") or REVISE).strip().upper()
            if state_raw in VALID_OVERRIDE_STATES:
                state = state_raw
            note = str(raw.get("note") or raw.get("feedback") or "").strip()
        out[name] = (state, note)
    return out


@dataclass
class Report:
    """Lineage of gates that actually ran, plus terminal state."""

    lineage: list[GateResult] = field(default_factory=list)
    final_state: str = PASS
    blocked_at: str | None = None
    proposal: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage": [g.to_dict() for g in self.lineage],
            "final_state": self.final_state,
            "blocked_at": self.blocked_at,
            "proposal": dict(self.proposal),
        }


class DecisionGATE:
    """Pre-execution filter. Not predictive, advisory, or prescriptive."""

    def run(
        self,
        proposal: Proposal | Mapping[str, Any],
        overrides: Mapping[str, Any] | None = None,
    ) -> Report:
        if isinstance(proposal, Proposal):
            prop = proposal.normalized()
        else:
            prop = Proposal.from_dict(dict(proposal))
        forced = _coerce_overrides(overrides)
        lineage: list[GateResult] = []
        final_state = PASS
        blocked_at: str | None = None

        for fn in GATE_FUNCS:
            result = fn(prop)
            if result.name in forced:
                state, note = forced[result.name]
                auto = result.state
                feedback = result.feedback
                if note:
                    feedback = (
                        f"{feedback} Human override to {state}: {note}"
                    )
                else:
                    feedback = (
                        f"{feedback} Human override to {state} "
                        "(no note supplied)."
                    )
                result = GateResult(
                    name=result.name,
                    state=state,
                    feedback=feedback,
                    overridden=True,
                    automatic_state=auto,
                    override_note=note or None,
                )
            lineage.append(result)
            if result.state != PASS:
                final_state = result.state
                if result.state == BLOCK:
                    blocked_at = result.name
                break

        return Report(
            lineage=lineage,
            final_state=final_state,
            blocked_at=blocked_at,
            proposal=prop.to_dict(),
        )
