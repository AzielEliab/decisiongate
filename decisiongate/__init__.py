"""DecisionGATE: a lightweight ethical pre-execution filter.

July 2026 whitepaper implementation by Aziel Eliab.

Not predictive, advisory, or prescriptive. A proposal does not pass
unless it survives structured scrutiny through five sequential gates:
Definition, Evidence, Impact, Integrity, Responsibility.

Freedom without clarity is chaos. Clarity without force is wisdom.

Forks are welcome and always allowed.
"""

from __future__ import annotations

from decisiongate.engine import DecisionGATE, Report
from decisiongate.gates import BLOCK, PASS, REVISE, GateResult
from decisiongate.proposal import Proposal

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "BLOCK",
    "DecisionGATE",
    "GateResult",
    "PASS",
    "Proposal",
    "REVISE",
    "Report",
    "__version__",
]
