"""TAED trust-aware phishing detection components."""

from .trust_gate import compute_trust_score, should_escalate
from .explanation import get_explanation_features

__all__ = [
    "compute_trust_score",
    "should_escalate",
    "get_explanation_features",
]
