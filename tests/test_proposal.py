"""Proposal normalize / from_dict."""

from __future__ import annotations

from decisiongate.proposal import Proposal


def test_from_dict_drops_blank_list_items() -> None:
    p = Proposal.from_dict(
        {
            "statement": "  hello  ",
            "evidence": ["a", "", "  "],
            "impacts_positive": "one\ntwo",
            "accountable": "  Name  ",
        }
    )
    assert p.statement == "hello"
    assert p.evidence == ["a"]
    assert p.impacts_positive == ["one", "two"]
    assert p.accountable_person == "Name"


def test_to_dict_roundtrip() -> None:
    p = Proposal(statement="x", evidence=["e"], accountable_person="A")
    q = Proposal.from_dict(p.to_dict())
    assert q.to_dict() == p.to_dict()
