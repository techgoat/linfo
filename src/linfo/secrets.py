"""Secure API key retrieval (OWASP Secrets Management).

Provider-aware resolution lives in ``linfo.providers``. This module keeps a
small, xAI-oriented surface for backward compatibility.
"""

from __future__ import annotations

from linfo.providers import resolve_llm_config


def get_api_key(provider: str | None = None) -> str:
    """Securely retrieve an API key for the given (or default) provider.

    Follows OWASP Secrets Management: never hard-coded, fail closed,
    and the value is never placed in logs or history.

    Default provider is xAI. Also accepts AI_API_KEY / LINFO_API_KEY via the
    provider key chain (see ``linfo.providers``).
    """
    cfg = resolve_llm_config(provider=provider, require_key=True)
    if not cfg.api_key:
        raise ValueError("API key resolution failed (empty key).")
    return cfg.api_key


# Back-compat alias used in older docs / internal call sites
_get_api_key = get_api_key
