"""Static / offline (non-agentic) helpers — no LLM, no API key."""

from __future__ import annotations

from linfo.models import Distro


def build_static_summary(distro: Distro) -> str:
    """Build a short Markdown summary from curated static fields only."""
    data = distro.data or {}
    if not data:
        return ""

    lines = [
        f"### {data.get('display_name') or distro.name}",
        "",
        f"- **Architecture:** {distro.arch}",
    ]

    field_labels = [
        ("pkg_manager", "Package manager"),
        ("default_desktop", "Desktop"),
        ("release_model", "Release model"),
        ("build_system", "Build system"),
        ("typical_footprint", "Typical footprint"),
        ("init_system", "Init system"),
        ("update_mechanism", "Updates"),
        ("common_targets", "Common targets"),
        ("official_site", "Website"),
        ("download_url", "Download"),
    ]
    for key, label in field_labels:
        val = data.get(key)
        if val:
            lines.append(f"- **{label}:** {val}")

    lines.extend(
        [
            "",
            "_Static curated data (offline / non-agentic mode — no LLM)._",
        ]
    )
    return "\n".join(lines)


def offline_missing_data_message(name: str, *, embedded: bool = False) -> str:
    """User-facing error when offline mode has no static entry."""
    db = "embedded or desktop static databases" if embedded else "static database"
    return (
        f"Offline mode: no curated data for '{name}' in the {db}. "
        "Use agentic mode with a configured provider API key "
        "(default: XAI_API_KEY for xAI), pick a known distro "
        f"(e.g. Ubuntu, Fedora, OpenWrt with --embedded), "
        "or add an entry to DISTRO_DATA"
        + (" / EMBEDDED_DISTRO_DATA" if embedded else "")
        + "."
    )
