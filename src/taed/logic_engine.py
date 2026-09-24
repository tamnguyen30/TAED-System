URGENCY_TERMS = ["immediately", "urgent", "24 hours", "suspended", "lockout", "restricted", "unauthorized", "at risk", "terminate", "warning", "asap"]
GREED_TERMS = ["winner", "congratulations", "won", "prize", "gift card", "reward", "lottery", "claim your", "$"]
ACTION_TERMS = ["click here", "login", "sign in", "verify", "update", "confirm", "secure your", "visit our", "portal", "claim", "link"]
SECRECY_TERMS = ["discreet", "confidential", "can't talk", "conference call", "meeting", "personal cell", "personal number", "do not email", "private"]
FINANCIAL_TERMS = ["financial matter", "transfer", "wire", "bank", "expense", "payment", "process", "gift card", "funds", "invoice"]


def scan_for_semantic_threats(text):
    """Rule-based semantic verification stage."""
    if not isinstance(text, str):
        return False

    text_lower = text.lower()

    has_urgency = any(term in text_lower for term in URGENCY_TERMS)
    has_greed = any(term in text_lower for term in GREED_TERMS)
    has_action = any(term in text_lower for term in ACTION_TERMS)
    has_secrecy = any(term in text_lower for term in SECRECY_TERMS)
    has_financial = any(term in text_lower for term in FINANCIAL_TERMS)

    if has_action and (has_urgency or has_greed):
        return True

    if has_secrecy and (has_financial or "reply" in text_lower):
        return True

    return False
