"""Machine-readable output helpers (--json)."""

from __future__ import annotations

import json
import sys
from typing import Any

from linfo.models import Distro


def build_result_payload(
    distro: Distro,
    *,
    response: str | None,
    style: str,
    brief: bool,
    embedded: bool,
    random_mode: bool = False,
    offline: bool = False,
    provider: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Build a stable JSON-serializable result object."""
    static = None
    if distro.data:
        # Avoid dumping huge multi-line ASCII into scripts unless present
        static = {
            k: v
            for k, v in distro.data.items()
            if k != "ascii_logo"
        }
        static["has_ascii_logo"] = "ascii_logo" in distro.data

    return {
        "name": distro.name,
        "arch": distro.arch,
        "level": distro.level,
        "topics": distro.topics,
        "style": style,
        "brief": brief,
        "embedded": embedded,
        "offline": offline,
        "provider": provider,
        "model": model,
        "random_mode": random_mode,
        "static_data": static,
        "response": response or "",
    }


def emit_json(payload: dict[str, Any]) -> None:
    """Write pretty JSON to stdout (for piping / scripting)."""
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
