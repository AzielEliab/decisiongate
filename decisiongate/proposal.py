"""Proposal record for DecisionGATE.

A proposal is a concrete action under scrutiny. It is not a prediction,
a recommendation, or a prescription. Fields are the material the five
gates inspect. Empty or blank list items are dropped on normalize.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [p.strip() for p in value.replace("\r\n", "\n").split("\n")]
        if len(parts) == 1 and ";" in parts[0]:
            parts = [p.strip() for p in parts[0].split(";")]
        return [p for p in parts if p]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        out: list[str] = []
        for item in value:
            text = _as_str(item).strip()
            if text:
                out.append(text)
        return out
    text = _as_str(value).strip()
    return [text] if text else []


@dataclass
class Proposal:
    """Concrete unambiguous proposal presented to the five gates."""

    statement: str = ""
    evidence: list[str] = field(default_factory=list)
    impacts_positive: list[str] = field(default_factory=list)
    impacts_negative: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    commitments: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    accountable_person: str = ""

    def normalized(self) -> "Proposal":
        return Proposal(
            statement=_as_str(self.statement).strip(),
            evidence=_as_list(self.evidence),
            impacts_positive=_as_list(self.impacts_positive),
            impacts_negative=_as_list(self.impacts_negative),
            values=_as_list(self.values),
            commitments=_as_list(self.commitments),
            constraints=_as_list(self.constraints),
            accountable_person=_as_str(self.accountable_person).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        p = self.normalized()
        return {
            "statement": p.statement,
            "evidence": list(p.evidence),
            "impacts_positive": list(p.impacts_positive),
            "impacts_negative": list(p.impacts_negative),
            "values": list(p.values),
            "commitments": list(p.commitments),
            "constraints": list(p.constraints),
            "accountable_person": p.accountable_person,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Proposal":
        raw = data if isinstance(data, dict) else {}
        return cls(
            statement=_as_str(raw.get("statement", "")),
            evidence=_as_list(raw.get("evidence")),
            impacts_positive=_as_list(
                raw.get("impacts_positive", raw.get("impact_pos"))
            ),
            impacts_negative=_as_list(
                raw.get("impacts_negative", raw.get("impact_neg"))
            ),
            values=_as_list(raw.get("values")),
            commitments=_as_list(raw.get("commitments")),
            constraints=_as_list(raw.get("constraints")),
            accountable_person=_as_str(
                raw.get("accountable_person", raw.get("accountable", ""))
            ),
        ).normalized()
