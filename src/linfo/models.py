"""Core value objects for linfo (Arjan-style small dataclasses)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from linfo.data import get_distro_data


@dataclass
class Distro:
    """Small dataclass for a distro lookup target + its (optional) static data."""

    name: str
    arch: str = "x86_64"
    data: dict[str, str] | None = None
    level: str | None = None
    topics: str | None = None
    embedded: bool = False

    @classmethod
    def from_name(
        cls,
        name: str,
        arch: str = "x86_64",
        *,
        embedded: bool = False,
    ) -> Distro:
        data = get_distro_data(name, embedded=embedded)
        return cls(name=name, arch=arch, data=data, embedded=embedded)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Distro:
        embedded = bool(getattr(args, "embedded", False))
        name = getattr(args, "distro", "") or ""
        data = get_distro_data(name, embedded=embedded) if name else None
        return cls(
            name=name,
            arch=getattr(args, "arch", None) or "x86_64",
            data=data,
            level=getattr(args, "level", None),
            topics=getattr(args, "topics", None),
            embedded=embedded,
        )
