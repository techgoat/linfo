"""Rich terminal rendering for distro facts and LLM narratives."""

from __future__ import annotations

from dataclasses import dataclass, field

from rich.columns import Columns
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from linfo.models import Distro

# Shared console instance used by CLI orchestration and default renderer
console = Console()


@dataclass
class DistroRenderer:
    """Small renderer dataclass. Encapsulates style/brief/embedded choices and Rich rendering."""

    console: Console = field(default_factory=lambda: console)
    style: str = "markdown"  # "fetch" or "markdown"
    brief: bool = False
    embedded: bool = False

    def render(self, distro: Distro, response: str | None = None) -> None:
        if self.brief:
            # Brief mode: always compact; fetch if static data else compact summary
            if distro.data:
                self._render_fetch(distro, response)
            else:
                self._render_brief_summary(distro, response)
            return

        use_fetch = self.style == "fetch"
        if use_fetch and distro.data:
            self._render_fetch(distro, response)
            self._render_in_depth(distro, response)
        else:
            self._render_markdown(distro, response)
            if distro.data:
                dl = distro.data.get("download_url")
                if dl:
                    self.console.print(
                        Text.assemble(
                            ("Official download: ", "bold green"),
                            (dl, "underline blue"),
                        )
                    )
                    self.console.print()

    def _render_fetch(self, distro: Distro, blurb: str | None = None) -> None:
        """Internal fastfetch/neofetch style (logo + facts + download)."""
        data = distro.data or {}
        logo = data.get("ascii_logo", "   Linux   ").strip("\n")
        logo_text = Text(logo, style=data.get("color", "bright_cyan"))

        title_name = distro.name
        if self.embedded or distro.embedded:
            title_name = f"{distro.name} [embedded]"

        logo_panel = Panel(
            logo_text,
            title=Text(title_name, style="bold"),
            border_style=data.get("color", "dim"),
            padding=(0, 1),
            expand=False,
        )

        facts: list[Text] = [
            Text.assemble(("Distro    ", "bold cyan"), distro.name),
            Text.assemble(("Arch      ", "bold cyan"), distro.arch),
        ]

        if self.embedded or distro.embedded:
            facts.extend(
                [
                    Text.assemble(
                        ("Build     ", "bold cyan"),
                        data.get("build_system", "—"),
                    ),
                    Text.assemble(
                        ("Footprint ", "bold cyan"),
                        data.get("typical_footprint", "—"),
                    ),
                    Text.assemble(
                        ("Init      ", "bold cyan"),
                        data.get("init_system", "—"),
                    ),
                    Text.assemble(
                        ("Updates   ", "bold cyan"),
                        data.get("update_mechanism", "—"),
                    ),
                    Text.assemble(
                        ("Targets   ", "bold cyan"),
                        data.get("common_targets", "—"),
                    ),
                    Text.assemble(
                        ("PM        ", "bold cyan"),
                        data.get("pkg_manager", "—"),
                    ),
                ]
            )
        else:
            facts.extend(
                [
                    Text.assemble(
                        ("PM        ", "bold cyan"),
                        data.get("pkg_manager", "—"),
                    ),
                    Text.assemble(
                        ("Desktop   ", "bold cyan"),
                        data.get("default_desktop", "Varies"),
                    ),
                    Text.assemble(
                        ("Release   ", "bold cyan"),
                        data.get("release_model", "—"),
                    ),
                ]
            )

        facts.extend(
            [
                Text.assemble(
                    ("Website   ", "bold cyan"),
                    data.get("official_site", "—"),
                ),
                Text.assemble(
                    ("Download  ", "bold green"),
                    data.get("download_url", "—"),
                ),
            ]
        )

        info_title = "Embedded Info" if (self.embedded or distro.embedded) else "System Info"
        info_group = Group(*facts)
        info_panel = Panel(
            info_group,
            title=info_title,
            border_style="dim",
            padding=(0, 1),
            expand=False,
        )

        self.console.print(
            Columns(
                [logo_panel, info_panel],
                expand=False,
                align="left",
                padding=(0, 2),
            )
        )
        self.console.print()

    def _render_brief_summary(self, distro: Distro, response: str | None) -> None:
        """Compact view for distros without static data."""
        prefix = "Brief (embedded): " if (self.embedded or distro.embedded) else "Brief: "
        title = Text.assemble(
            (prefix, "bold yellow"),
            (distro.name or "Unknown Distro", "bold cyan"),
            (f" ({distro.arch})", "dim"),
        )
        self.console.print(Panel(title, border_style="yellow", padding=(0, 1)))

        if response:
            self.console.print(Markdown(response))
        self.console.print()

    def _render_in_depth(self, distro: Distro, response: str | None) -> None:
        """Show full LLM response as In-Depth panel (used after fetch when not brief)."""
        if not response:
            return
        level = distro.level or "general"
        detail_title = Text.assemble(
            ("In-Depth: ", "bold white"),
            (distro.name, "bold cyan"),
            (f"  •  {distro.arch}", "dim"),
        )
        detail_sub = Text.assemble(
            ("Level: ", "dim"),
            (level, "bold yellow"),
            ("   •   Topics: ", "dim"),
            (distro.topics or "overview + features", "italic"),
        )
        md = Markdown(response)
        detail_panel = Panel(
            md,
            title=detail_title,
            subtitle=detail_sub,
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(detail_panel)
        self.console.print()

    def _render_markdown(self, distro: Distro, response: str | None) -> None:
        """Traditional rich Markdown panel."""
        if not response:
            return
        level = distro.level or "general"
        title = Text.assemble(
            ("Linux Distro Info: ", "bold white"),
            (distro.name, "bold cyan"),
            (f"  •  {distro.arch}", "dim"),
        )
        subtitle = Text.assemble(
            ("Expertise: ", "dim"),
            (level, "bold yellow"),
            ("   •   Topics: ", "dim"),
            (distro.topics or "default", "italic"),
        )
        md = Markdown(response)
        panel = Panel(
            md,
            title=title,
            subtitle=subtitle,
            border_style="bright_blue",
            padding=(1, 2),
            expand=True,
        )
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()
