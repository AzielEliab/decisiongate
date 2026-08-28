"""Five sequential DecisionGATE gates.

Deterministic heuristics. No ML. Documented rules, kept small and tested.

Each gate returns GateResult(name, state, feedback) where state is one of
PASS, REVISE, BLOCK.

REVISE includes specific feedback the author can act on.
BLOCK cannot be remedied without changing the proposal's nature.

Rules
-----
1. Definition
   BLOCK if the statement is empty.
   REVISE if the statement has fewer than 12 words, or if after removing
   the hedges {maybe, somehow, stuff, things} there is no verb+object
   (at least one verb-like token and one other content token).
2. Evidence
   REVISE if the evidence list is empty.
3. Impact
   REVISE if either the positive or the negative impact list is empty.
4. Integrity
   REVISE if the values list is empty.
   BLOCK if the statement clearly contradicts a provided constraint
   (simple substring / negation check: a prohibition whose payload
   appears in the statement).
5. Responsibility
   BLOCK if accountable_person is blank.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from decisiongate.proposal import Proposal

PASS = "PASS"
REVISE = "REVISE"
BLOCK = "BLOCK"

HEDGES = frozenset({"maybe", "somehow", "stuff", "things"})

# Small closed verb list plus suffix checks. Not an NLP parser.
_COMMON_VERBS = frozenset(
    {
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "am",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "shall",
        "should",
        "can",
        "could",
        "must",
        "need",
        "needs",
        "make",
        "makes",
        "made",
        "take",
        "takes",
        "took",
        "give",
        "gives",
        "gave",
        "go",
        "goes",
        "went",
        "come",
        "keep",
        "put",
        "use",
        "uses",
        "used",
        "set",
        "get",
        "let",
        "allow",
        "allows",
        "publish",
        "release",
        "releases",
        "deploy",
        "ship",
        "open",
        "close",
        "create",
        "created",
        "delete",
        "write",
        "read",
        "run",
        "execute",
        "adopt",
        "reject",
        "approve",
        "block",
        "collect",
        "store",
        "share",
        "send",
        "build",
        "launch",
        "hire",
        "spend",
        "buy",
        "sell",
        "migrate",
        "replace",
        "update",
        "install",
        "announce",
        "commit",
        "sign",
        "fund",
        "grant",
        "revoke",
        "host",
        "serve",
        "bind",
        "filter",
        "record",
        "name",
        "assign",
        "document",
        "provide",
        "provides",
        "include",
        "includes",
        "add",
        "remove",
        "stop",
        "start",
        "move",
        "change",
        "apply",
        "submit",
        "accept",
        "refuse",
        "pay",
        "offer",
        "request",
        "require",
        "requires",
        "implement",
        "implements",
    }
)

_NEGATION_MARKERS = (
    "do not ",
    "don't ",
    "does not ",
    "doesn't ",
    "must not ",
    "cannot ",
    "can't ",
    "never ",
    "no ",
    "not ",
    "without ",
)

_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*")


@dataclass
class GateResult:
    """Outcome of one gate. ``state`` is PASS, REVISE, or BLOCK."""

    name: str
    state: str
    feedback: str
    overridden: bool = False
    automatic_state: str | None = None
    override_note: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "state": self.state,
            "feedback": self.feedback,
        }
        if self.overridden:
            payload["overridden"] = True
            if self.automatic_state:
                payload["automatic_state"] = self.automatic_state
            if self.override_note:
                payload["override_note"] = self.override_note
        return payload


def tokenize(text: str) -> list[str]:
    """Lowercased word tokens; punctuation stripped."""
    return _WORD_RE.findall(text.lower()) if text else []


def _looks_like_verb(token: str) -> bool:
    if token in _COMMON_VERBS:
        return True
    if len(token) > 4 and token.endswith(("ing", "ize", "ise", "ify")):
        return True
    if len(token) > 4 and token.endswith("ed"):
        return True
    return False


def has_verb_and_object(tokens: list[str]) -> bool:
    """True when non-hedge tokens include a verb-like word and one other token."""
    content = [t for t in tokens if t not in HEDGES]
    if len(content) < 2:
        return False
    return any(_looks_like_verb(t) for t in content)


def gate_definition(proposal: Proposal) -> GateResult:
    statement = proposal.statement.strip()
    if not statement:
        return GateResult(
            name="Definition",
            state=BLOCK,
            feedback=(
                "Statement is empty. A proposal with no concrete statement "
                "cannot pass Definition. Write an unambiguous action with a "
                "verb and an object, at least 12 words."
            ),
        )
    tokens = tokenize(statement)
    if len(tokens) < 12:
        return GateResult(
            name="Definition",
            state=REVISE,
            feedback=(
                f"Statement has {len(tokens)} word(s); Definition requires "
                "at least 12. Expand into a concrete, unambiguous proposal "
                "(who does what, to what, under what bound)."
            ),
        )
    if not has_verb_and_object(tokens):
        return GateResult(
            name="Definition",
            state=REVISE,
            feedback=(
                "Statement is hedge-only or lacks a verb+object after removing "
                "maybe/somehow/stuff/things. Name a specific action and its object."
            ),
        )
    return GateResult(
        name="Definition",
        state=PASS,
        feedback="Statement is concrete enough to scrutinize (length, verb+object).",
    )


def gate_evidence(proposal: Proposal) -> GateResult:
    items = [e for e in proposal.evidence if e.strip()]
    if not items:
        return GateResult(
            name="Evidence",
            state=REVISE,
            feedback=(
                "Evidence list is empty. Identify at least one fact, datum, "
                "or observation that grounds the statement. Ungrounded "
                "assertions do not pass Evidence."
            ),
        )
    return GateResult(
        name="Evidence",
        state=PASS,
        feedback=f"{len(items)} evidence item(s) identified.",
    )


def gate_impact(proposal: Proposal) -> GateResult:
    pos = [i for i in proposal.impacts_positive if i.strip()]
    neg = [i for i in proposal.impacts_negative if i.strip()]
    missing: list[str] = []
    if not pos:
        missing.append("positive")
    if not neg:
        missing.append("negative")
    if missing:
        which = " and ".join(missing)
        return GateResult(
            name="Impact",
            state=REVISE,
            feedback=(
                f"Impact list(s) empty: {which}. Name who or what is affected "
                "on both the positive and the negative side. Hidden impacts "
                "do not pass Impact."
            ),
        )
    return GateResult(
        name="Impact",
        state=PASS,
        feedback=(
            f"{len(pos)} positive and {len(neg)} negative impact(s) named."
        ),
    )


def _constraint_payload(constraint: str) -> str | None:
    """If ``constraint`` is a prohibition, return the forbidden fragment."""
    text = " ".join(constraint.lower().split())
    if not text:
        return None
    found = False
    remainder = f" {text} "
    for marker in _NEGATION_MARKERS:
        padded = marker if marker.startswith(" ") else f" {marker}"
        if padded in remainder or remainder.lstrip().startswith(marker):
            found = True
            remainder = remainder.replace(padded, " ")
            if remainder.lstrip().startswith(marker):
                remainder = " " + remainder.lstrip()[len(marker) :]
    payload = " ".join(remainder.split())
    if found and payload:
        return payload
    return None


def statement_contradicts_constraint(statement: str, constraint: str) -> bool:
    """Simple substring/negation check. No parser, no ML."""
    payload = _constraint_payload(constraint)
    if not payload:
        return False
    hay = " ".join(statement.lower().split())
    return payload in hay


def gate_integrity(proposal: Proposal) -> GateResult:
    values = [v for v in proposal.values if v.strip()]
    if not values:
        return GateResult(
            name="Integrity",
            state=REVISE,
            feedback=(
                "Values list is empty. Integrity requires stated values so "
                "the proposal can be checked against them."
            ),
        )
    hits: list[str] = []
    for constraint in proposal.constraints:
        if statement_contradicts_constraint(proposal.statement, constraint):
            hits.append(constraint)
    if hits:
        shown = hits[0]
        return GateResult(
            name="Integrity",
            state=BLOCK,
            feedback=(
                "Statement contradicts a provided constraint "
                f"({shown!r}). A contradiction of this kind cannot pass "
                "Integrity without changing the proposal's nature."
            ),
        )
    return GateResult(
        name="Integrity",
        state=PASS,
        feedback=(
            f"{len(values)} value(s) stated; no constraint contradiction detected."
        ),
    )


def gate_responsibility(proposal: Proposal) -> GateResult:
    owner = proposal.accountable_person.strip()
    if not owner:
        return GateResult(
            name="Responsibility",
            state=BLOCK,
            feedback=(
                "Accountable person is blank. Diffuse or absent ownership "
                "cannot pass Responsibility. Name one accountable owner."
            ),
        )
    return GateResult(
        name="Responsibility",
        state=PASS,
        feedback=f"Accountable owner named: {owner}.",
    )


GATE_ORDER: tuple[str, ...] = (
    "Definition",
    "Evidence",
    "Impact",
    "Integrity",
    "Responsibility",
)

GATE_FUNCS: tuple[Callable[[Proposal], GateResult], ...] = (
    gate_definition,
    gate_evidence,
    gate_impact,
    gate_integrity,
    gate_responsibility,
)
