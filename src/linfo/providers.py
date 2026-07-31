"""LLM provider registry and credential resolution.

xAI is the project default. Other OpenAI-compatible endpoints are supported
via provider selection + env / CLI overrides. Secrets are never logged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSpec:
    """Static description of an OpenAI-compatible LLM backend."""

    id: str
    display_name: str
    base_url: str
    default_model: str
    key_env_vars: tuple[str, ...]
    model_env_vars: tuple[str, ...] = ()
    requires_key: bool = True
    min_key_length: int = 8
    # When requires_key is False (e.g. Ollama), use this placeholder if unset
    placeholder_key: str = "not-needed"


# Default provider when LINFO_LLM_PROVIDER / --provider is unset
DEFAULT_PROVIDER = "xai"

PROVIDERS: dict[str, ProviderSpec] = {
    "xai": ProviderSpec(
        id="xai",
        display_name="xAI (Grok)",
        base_url="https://api.x.ai/v1",
        default_model="grok-4",
        key_env_vars=("XAI_API_KEY", "AI_API_KEY", "LINFO_API_KEY"),
        model_env_vars=("XAI_MODEL", "LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=True,
        min_key_length=20,
    ),
    "openai": ProviderSpec(
        id="openai",
        display_name="OpenAI",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        key_env_vars=("OPENAI_API_KEY", "AI_API_KEY", "LINFO_API_KEY"),
        model_env_vars=("OPENAI_MODEL", "LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=True,
        min_key_length=20,
    ),
    "groq": ProviderSpec(
        id="groq",
        display_name="Groq",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        key_env_vars=("GROQ_API_KEY", "AI_API_KEY", "LINFO_API_KEY"),
        model_env_vars=("GROQ_MODEL", "LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=True,
        min_key_length=20,
    ),
    "openrouter": ProviderSpec(
        id="openrouter",
        display_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        default_model="openai/gpt-4o-mini",
        key_env_vars=("OPENROUTER_API_KEY", "AI_API_KEY", "LINFO_API_KEY"),
        model_env_vars=("OPENROUTER_MODEL", "LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=True,
        min_key_length=20,
    ),
    "ollama": ProviderSpec(
        id="ollama",
        display_name="Ollama (local)",
        base_url="http://127.0.0.1:11434/v1",
        default_model="llama3.2",
        key_env_vars=("OLLAMA_API_KEY", "AI_API_KEY", "LINFO_API_KEY"),
        model_env_vars=("OLLAMA_MODEL", "LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=False,
        min_key_length=1,
        placeholder_key="ollama",
    ),
    "custom": ProviderSpec(
        id="custom",
        display_name="Custom OpenAI-compatible endpoint",
        base_url="",  # must come from LINFO_LLM_BASE_URL or --base-url
        default_model="gpt-4o-mini",
        key_env_vars=("AI_API_KEY", "LINFO_API_KEY", "OPENAI_API_KEY"),
        model_env_vars=("LINFO_LLM_MODEL", "AI_MODEL"),
        requires_key=True,
        min_key_length=8,
    ),
}


@dataclass(frozen=True)
class LLMConfig:
    """Resolved runtime LLM settings (safe to pass around; do not log api_key)."""

    provider: str
    base_url: str
    model: str
    api_key: str | None
    requires_key: bool
    key_source: str | None = None  # env var name that supplied the key, if any

    @property
    def has_credentials(self) -> bool:
        """True if this config can attempt an agentic call."""
        if not self.requires_key:
            return bool(self.base_url and self.model)
        return bool(self.api_key and self.base_url and self.model)


def list_provider_ids() -> list[str]:
    """Return sorted provider ids for CLI choices / docs."""
    return sorted(PROVIDERS.keys())


def get_provider_spec(provider_id: str) -> ProviderSpec:
    """Look up a provider; raises ValueError if unknown."""
    key = (provider_id or DEFAULT_PROVIDER).strip().lower()
    if key not in PROVIDERS:
        known = ", ".join(list_provider_ids())
        raise ValueError(f"Unknown LLM provider '{provider_id}'. Known: {known}")
    return PROVIDERS[key]


def _first_env(names: tuple[str, ...]) -> tuple[str | None, str | None]:
    """Return (value, env_var_name) for the first set env var in names."""
    for name in names:
        val = os.getenv(name)
        if val is not None and str(val).strip():
            return str(val).strip(), name
    return None, None


def resolve_provider_id(cli_provider: str | None = None) -> str:
    """Resolve provider id: CLI > LINFO_LLM_PROVIDER > default xai."""
    if cli_provider and str(cli_provider).strip():
        return str(cli_provider).strip().lower()
    env = os.getenv("LINFO_LLM_PROVIDER") or os.getenv("AI_PROVIDER")
    if env and env.strip():
        return env.strip().lower()
    return DEFAULT_PROVIDER


def peek_api_key(provider_id: str | None = None) -> tuple[str | None, str | None]:
    """Non-raising key peek for a provider. Returns (key, source_env_name)."""
    spec = get_provider_spec(resolve_provider_id(provider_id))
    key, source = _first_env(spec.key_env_vars)
    if key is None and not spec.requires_key:
        return spec.placeholder_key, None
    return key, source


def has_usable_credentials(
    provider_id: str | None = None,
    *,
    base_url: str | None = None,
) -> bool:
    """Whether agentic mode can run for this provider without prompting for a key."""
    try:
        cfg = resolve_llm_config(
            provider=provider_id,
            model=None,
            base_url=base_url,
            require_key=False,
        )
    except ValueError:
        return False
    if not cfg.base_url:
        return False
    if cfg.requires_key and not cfg.api_key:
        return False
    if cfg.requires_key and cfg.api_key and len(cfg.api_key) < get_provider_spec(cfg.provider).min_key_length:
        return False
    return True


def resolve_llm_config(
    *,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    require_key: bool = True,
) -> LLMConfig:
    """Resolve provider, model, base URL, and API key.

    Args:
        provider: CLI/provider id override.
        model: CLI model override.
        base_url: CLI base URL override (also env LINFO_LLM_BASE_URL).
        require_key: If True, raise when a required key is missing/invalid.

    Returns:
        LLMConfig (api_key may be None if require_key is False and missing).
    """
    provider_id = resolve_provider_id(provider)
    spec = get_provider_spec(provider_id)

    env_base = os.getenv("LINFO_LLM_BASE_URL") or os.getenv("AI_BASE_URL")
    resolved_base = (base_url or env_base or spec.base_url or "").strip()
    if provider_id == "custom" and not resolved_base:
        if require_key:
            raise ValueError(
                "Provider 'custom' requires --base-url or LINFO_LLM_BASE_URL "
                "(OpenAI-compatible API root, e.g. https://host/v1)."
            )

    # Model: CLI > provider model env > LINFO_LLM_MODEL > provider default
    resolved_model = (model or "").strip() if model else ""
    if not resolved_model:
        env_model, _ = _first_env(spec.model_env_vars)
        resolved_model = env_model or spec.default_model

    key, key_source = _first_env(spec.key_env_vars)
    if key is None and not spec.requires_key:
        key = spec.placeholder_key
        key_source = None

    if spec.requires_key:
        if not key:
            if require_key:
                primary = spec.key_env_vars[0]
                alts = ", ".join(spec.key_env_vars[1:]) if len(spec.key_env_vars) > 1 else "none"
                raise ValueError(
                    f"No API key found for provider '{provider_id}' ({spec.display_name}). "
                    f"Set {primary}"
                    + (f" (or {alts})" if alts != "none" else "")
                    + ", or use --offline for static-only mode without an LLM."
                )
        elif len(key) < spec.min_key_length:
            if require_key:
                src = key_source or "API key"
                raise ValueError(
                    f"{src} for provider '{provider_id}' appears invalid "
                    f"(too short; expected at least {spec.min_key_length} characters)."
                )
            key = None
            key_source = None

    return LLMConfig(
        provider=provider_id,
        base_url=resolved_base,
        model=resolved_model,
        api_key=key,
        requires_key=spec.requires_key,
        key_source=key_source,
    )


def provider_help_text() -> str:
    """Short multi-line help for --provider."""
    lines = []
    for pid in list_provider_ids():
        p = PROVIDERS[pid]
        keys = "/".join(p.key_env_vars[:2])
        lines.append(f"{pid} ({p.display_name}; keys: {keys})")
    return "LLM provider. " + "; ".join(lines) + f". Default: {DEFAULT_PROVIDER}."
