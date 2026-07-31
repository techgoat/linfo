"""Secure API key retrieval (OWASP Secrets Management)."""

from __future__ import annotations

import os


def get_api_key() -> str:
    """Securely retrieve the xAI API key.

    Follows OWASP Secrets Management: never hard-coded, fail closed,
    and the value is never placed in logs or history.
    """
    key = os.getenv("XAI_API_KEY")
    if not key:
        raise ValueError(
            "XAI_API_KEY environment variable not set. "
            "Add it to .env or your environment (never commit secrets)."
        )
    # Basic sanity (don't log the actual key)
    if len(key) < 20:
        raise ValueError("XAI_API_KEY appears invalid (too short).")
    return key


# Back-compat alias used in older docs / internal call sites
_get_api_key = get_api_key
