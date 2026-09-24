"""Trust-aware routing component for TAED."""


DEFAULT_ALPHA = 0.30
DEFAULT_BETA = 0.40
DEFAULT_GAMMA = 0.25
DEFAULT_THRESHOLD = 0.35


def compute_trust_score(confidence, fidelity, instability=0.05,
                        alpha=DEFAULT_ALPHA,
                        beta=DEFAULT_BETA,
                        gamma=DEFAULT_GAMMA):
    """Compute trust score from prediction and explanation signals."""
    score = (alpha * confidence) + (beta * fidelity) - (gamma * instability)
    return max(0.0, min(1.0, score))


def should_escalate(trust_score, threshold=DEFAULT_THRESHOLD):
    """Return whether additional analysis is required."""
    return trust_score < threshold
