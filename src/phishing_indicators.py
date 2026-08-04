"""
TAED Master Phishing Indicators Dictionary
==========================================
Canonical 30-term threat dictionary used across all TAED evaluation scripts.
Constructed from prior phishing detection literature before test set evaluation.
All scripts should import from this file to ensure consistency.

Categories (as described in paper Section 4.3.2):
  - Urgency language
  - Action verbs
  - Financial terminology
  - Credential requests
  - Authority impersonation
"""

PHISHING_INDICATORS = {
    # Urgency language (6 terms)
    "urgent", "immediate", "suspended", "unauthorized", "locked", "alert",

    # Action verbs (6 terms)
    "verify", "confirm", "update", "click", "login", "validate",

    # Financial terminology (6 terms)
    "invoice", "transfer", "wire", "billing", "payment", "bank",

    # Credential requests (6 terms)
    "password", "account", "security", "credentials", "authentication", "link",

    # Authority impersonation (6 terms)
    "notice", "required", "action", "service", "support", "department",
}

# Verify count on import
assert len(PHISHING_INDICATORS) == 30, (
    f"Expected 30 phishing indicators, got {len(PHISHING_INDICATORS)}"
)
