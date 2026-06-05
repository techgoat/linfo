#!/usr/bin/env python3
"""
src/linfo/main.py

linfo - Linux distro info CLI (fastfetch-style + rich LLM details).

An agentic CLI tool for retrieving tailored information about Linux distributions.
Developed with assistance from Grok Build (xAI).

Design notes (Arjan Codes inspired):
- Single Responsibility: separate concerns for data (DISTRO_DATA), rendering
  (DistroRenderer dataclass), agent orchestration (run_agent), secrets (_get_api_key).
- Security (OWASP Secrets + LLM Agentic): API keys never hardcoded, never logged,
  fetched just-in-time via _get_api_key. Tools are read-only. Limited agency.
- Output: fastfetch/neofetch-style via --style fetch or --brief (with ASCII + download for supported distros; compact summary for any distro).
- Project uses the recommended `src/` layout for clean packaging and to avoid
  import shadowing (as discussed in Arjan Codes' design guidance).

MIT License — see LICENSE file for details.
"""

import argparse
import json
import logging
import os
import time
from dataclasses import dataclass, field
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from dotenv import load_dotenv

from rich.columns import Columns
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

# Rich console for beautiful terminal output (single instance used by banner, errors, and renderer)
console = Console()


load_dotenv()


# llm = ChatOpenAI(
#    model="grok-4",  # grok-4 
#    api_key=os.getenv("XAI_API_KEY"),
#    base_url="https://api.x.ai/v1"
# )


HISTORY_FILE = 'query_history.json'

# Curated list of popular distros for the random feature
RANDOM_DISTROS = [
    ("Ubuntu", "x86_64"),
    ("Fedora", "x86_64"),
    ("Debian", "x86_64"),
    ("Arch Linux", "x86_64"),
    ("Linux Mint", "x86_64"),
    ("Pop!_OS", "x86_64"),
    ("openSUSE Tumbleweed", "x86_64"),
    ("NixOS", "x86_64"),
    ("Kali Linux", "x86_64"),
    ("AlmaLinux", "x86_64"),
    ("Rocky Linux", "x86_64"),
    ("Parrot Security", "x86_64"),
]

# Static data for fastfetch-style output + download links + ASCII (inspired by neofetch)
# Keys are normalized (lowercase, no spaces/punctuation)
DISTRO_DATA: dict[str, dict[str, str]] = {
    "ubuntu": {
        "display_name": "Ubuntu",
        "ascii_logo": r"""
               _
           ---(_)
         /        \\
        |   Ubuntu |
         \\        /
           `-----'
""",
        "color": "bright_red",
        "pkg_manager": "APT / dpkg + Snap",
        "default_desktop": "GNOME (default)",
        "official_site": "https://ubuntu.com",
        "download_url": "https://ubuntu.com/download/desktop",
        "release_model": "Point releases + LTS (2y/5y+)",
    },
    "fedora": {
        "display_name": "Fedora",
        "ascii_logo": r"""
      _____
     /     \\
    /   o   \\
   (    ---   )
    \\         /
     \\_______/
""",
        "color": "bright_blue",
        "pkg_manager": "DNF / RPM + Flatpak",
        "default_desktop": "GNOME (Workstation)",
        "official_site": "https://fedoraproject.org",
        "download_url": "https://fedoraproject.org/workstation/download/",
        "release_model": "6-month rapid releases",
    },
    "debian": {
        "display_name": "Debian",
        "ascii_logo": r"""
      .-.
     /   \\
    |  o  |
     \\   /
      '-'
""",
        "color": "red",
        "pkg_manager": "APT / dpkg",
        "default_desktop": "GNOME (varies by spin)",
        "official_site": "https://www.debian.org",
        "download_url": "https://www.debian.org/distrib/",
        "release_model": "Stable ~2 years, very conservative",
    },
    "archlinux": {
        "display_name": "Arch Linux",
        "ascii_logo": r"""
     .--.
    |o_o |
    |:_/ |
   //   \ \\
  (|     | )
 /'\_   _/`\
\___)=(___/
""",
        "color": "bright_cyan",
        "pkg_manager": "Pacman + AUR helpers",
        "default_desktop": "None (user chosen)",
        "official_site": "https://archlinux.org",
        "download_url": "https://archlinux.org/download/",
        "release_model": "Rolling release",
    },
    "linuxmint": {
        "display_name": "Linux Mint",
        "ascii_logo": r"""
      .--.
     /    \\
    | Mint |
     \\    /
      '--'
""",
        "color": "bright_green",
        "pkg_manager": "APT + Flatpak + AppImage",
        "default_desktop": "Cinnamon (default)",
        "official_site": "https://linuxmint.com",
        "download_url": "https://linuxmint.com/download.php",
        "release_model": "Based on Ubuntu LTS, 5y support",
    },
    "popos": {
        "display_name": "Pop!_OS",
        "ascii_logo": r"""
   ______
  /      \\
 |  Pop!  |
  \\______/
""",
        "color": "bright_magenta",
        "pkg_manager": "APT + Flatpak + AppImage",
        "default_desktop": "COSMIC (or GNOME)",
        "official_site": "https://pop.system76.com",
        "download_url": "https://pop.system76.com/",
        "release_model": "Ubuntu-based, 2 releases/year",
    },
    "opensusetumbleweed": {
        "display_name": "openSUSE Tumbleweed",
        "ascii_logo": r"""
    ____
   /    \\
  | open |
   \\____/
""",
        "color": "bright_yellow",
        "pkg_manager": "Zypper / RPM + transactional",
        "default_desktop": "KDE Plasma or GNOME",
        "official_site": "https://www.opensuse.org",
        "download_url": "https://get.opensuse.org/",
        "release_model": "Rolling release (Tumbleweed)",
    },
    "nixos": {
        "display_name": "NixOS",
        "ascii_logo": r"""
   ___
  /   \\
 | Nix |
  \\___/
""",
        "color": "bright_blue",
        "pkg_manager": "Nix (declarative)",
        "default_desktop": "Various (user configured)",
        "official_site": "https://nixos.org",
        "download_url": "https://nixos.org/download/",
        "release_model": "Rolling + declarative generations",
    },
    "kalilinux": {
        "display_name": "Kali Linux",
        "ascii_logo": r"""
   .--.
  /    \\
 | Kali |
  \\    /
   '--'
""",
        "color": "bright_red",
        "pkg_manager": "APT + custom repos",
        "default_desktop": "Xfce (default), GNOME, etc.",
        "official_site": "https://www.kali.org",
        "download_url": "https://www.kali.org/get-kali/",
        "release_model": "Rolling (Debian-based)",
    },
    "almalinux": {
        "display_name": "AlmaLinux",
        "ascii_logo": r"""
   ____
  /    \\
 | Alma |
  \\____/
""",
        "color": "bright_green",
        "pkg_manager": "DNF / RPM",
        "default_desktop": "GNOME (varies)",
        "official_site": "https://almalinux.org",
        "download_url": "https://almalinux.org/get-almalinux/",
        "release_model": "RHEL clone, 10y support",
    },
    "rockylinux": {
        "display_name": "Rocky Linux",
        "ascii_logo": r"""
   ____
  /    \\
 |Rocky|
  \\____/
""",
        "color": "bright_green",
        "pkg_manager": "DNF / RPM",
        "default_desktop": "GNOME (varies)",
        "official_site": "https://rockylinux.org",
        "download_url": "https://rockylinux.org/download",
        "release_model": "RHEL clone, community driven",
    },
    "parrotsecurity": {
        "display_name": "Parrot Security",
        "ascii_logo": r"""
   ____
  /    \\
 |Parrot|
  \\____/
""",
        "color": "bright_blue",
        "pkg_manager": "APT (Debian + Parrot repos)",
        "default_desktop": "MATE (customized)",
        "official_site": "https://parrotsec.org",
        "download_url": "https://parrotsec.org/download/",
        "release_model": "Rolling (Debian-based)",
    },
}

def normalize_distro_name(name: str) -> str:
    """Normalize distro name for lookup in DISTRO_DATA."""
    return (
        name.lower()
        .replace(" ", "")
        .replace("!", "")
        .replace("_", "")
        .replace("-", "")
        .replace(".", "")
    )

def get_distro_data(distro_name: str) -> dict | None:
    """Return static data for a distro (case/space tolerant)."""
    key = normalize_distro_name(distro_name)
    return DISTRO_DATA.get(key)


def _get_api_key() -> str:
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


@dataclass
class Distro:
    """Small dataclass for a distro lookup target + its (optional) static data."""
    name: str
    arch: str = "x86_64"
    data: dict[str, str] | None = None
    level: str | None = None
    topics: str | None = None

    @classmethod
    def from_name(cls, name: str, arch: str = "x86_64") -> "Distro":
        data = get_distro_data(name)
        return cls(name=name, arch=arch, data=data)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Distro":
        data = get_distro_data(args.distro) if getattr(args, "distro", None) else None
        return cls(
            name=getattr(args, "distro", "") or "",
            arch=getattr(args, "arch", None) or "x86_64",
            data=data,
            level=getattr(args, "level", None),
            topics=getattr(args, "topics", None),
        )


@dataclass
class DistroRenderer:
    """Small renderer dataclass. Encapsulates style/brief choices and Rich rendering."""
    console: Console = field(default_factory=lambda: console)
    style: str = "markdown"  # "fetch" or "markdown"
    brief: bool = False

    def render(self, distro: Distro, response: str | None = None) -> None:
        if self.brief:
            # Brief mode: always compact, use rich fetch if we have static data, else compact summary of LLM output
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
            # For non-brief also show download if we have static data
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

        logo_panel = Panel(
            logo_text,
            title=Text(distro.name, style="bold"),
            border_style=data.get("color", "dim"),
            padding=(0, 1),
            expand=False,
        )

        facts: list[Text] = [
            Text.assemble(("Distro    ", "bold cyan"), distro.name),
            Text.assemble(("Arch      ", "bold cyan"), distro.arch),
            Text.assemble(("PM        ", "bold cyan"), data.get("pkg_manager", "—")),
            Text.assemble(("Desktop   ", "bold cyan"), data.get("default_desktop", "Varies")),
            Text.assemble(("Release   ", "bold cyan"), data.get("release_model", "—")),
            Text.assemble(("Website   ", "bold cyan"), data.get("official_site", "—")),
            Text.assemble(("Download  ", "bold green"), data.get("download_url", "—")),
        ]

        info_group = Group(*facts)
        info_panel = Panel(
            info_group,
            title="System Info",
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
        """Compact view for distros without static data (e.g. --brief on arbitrary distros like Parrot Security).

        Shows a small header + the (hopefully concise, thanks to prompt) LLM response.
        """
        title = Text.assemble(
            ("Brief: ", "bold yellow"),
            (distro.name or "Unknown Distro", "bold cyan"),
            (f" ({distro.arch})", "dim"),
        )
        self.console.print(Panel(title, border_style="yellow", padding=(0, 1)))

        if response:
            # Render the response directly (Markdown will handle headings/lists nicely but in context of brief header)
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


def setup_logging(verbose: bool = False) -> None:
    """Configure logging.

    - Always writes full INFO logs to transaction_log.txt
    - Console (StreamHandler) only receives logs when --verbose is used.
    """
    # Remove any existing handlers (in case of re-runs in same process)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Always log everything to the file
    file_handler = logging.FileHandler('transaction_log.txt')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if verbose:
        # Verbose mode: also show INFO+ on the terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
    # else: console stays quiet (only errors/warnings if we add them later)

def load_history():
    """Load past queries from JSON file.

    Returns:
        list: List of past query dictionaries.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history, new_entry):
    """Append new query to history and save to JSON.

    Args:
        history (list): Current history list.
        new_entry (dict): New query entry to add.
    """
    history.append(new_entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)
    logging.info(f"Saved new entry to history: {new_entry}")

def validate_inputs(args):
    """Validate CLI arguments (level only — distro/arch are guaranteed by main()).

    Args:
        args (argparse.Namespace): Parsed arguments.

    Raises:
        ValueError: If validation fails.
    """
    if args.level and args.level not in ['beginner', 'intermediate', 'advanced', 'general']:
        raise ValueError("Expertise level must be one of: beginner, intermediate, advanced (or omit for general).")
    logging.info("Inputs validated successfully.")

def build_prompt(args, brief: bool = False):
    """Build the agent prompt based on arguments.

    Args:
        args (argparse.Namespace): Parsed arguments.
        brief (bool): If True, request a more concise response (used with --brief flag).

    Returns:
        str: Formatted prompt string.
    """
    topics = args.topics.split(',') if args.topics else ['basic overview', 'features', 'package management']
    level = args.level or 'general'

    if brief:
        prompt = (
            f"Provide a **concise** summary of information about the Linux distribution '{args.distro}' "
            f"for the '{args.arch}' architecture. Tailor the response for a {level} user. "
            f"Cover the following topics: {', '.join(topics)}. "
            "Focus on key facts only (e.g. package manager, desktop environments, target users, pros/cons, official site and download link if relevant). "
            "Keep the total response short and to-the-point. Use tools to fetch accurate, up-to-date info."
        )
    else:
        prompt = (
            f"Provide detailed information about the Linux distribution '{args.distro}' "
            f"for the '{args.arch}' architecture. Tailor the response for a {level} user. "
            f"Cover the following topics: {', '.join(topics)}. "
            "Include practical details such as who the distro is best suited for, "
            "key strengths/weaknesses, and any official resources. "
            "Use tools to fetch accurate, up-to-date info. Reason step-by-step."
        )
    logging.info(f"Built prompt: {prompt}")
    return prompt

def run_agent(prompt: str) -> str:
    """Initialize and run the LLM with tools using a manual tool-calling loop.

    The model may request tools (Wikipedia, DuckDuckGo). We execute them
    and feed results back until the model produces a final text response.

    Security note: API key is fetched securely inside _get_api_key and
    is never passed into the LLM context or logged.

    Args:
        prompt (str): The prompt for the agent.

    Returns:
        str: LLM's final response content.
    """
    # Secure key fetch (never logs the secret itself)
    api_key = _get_api_key()

    llm = ChatOpenAI(
        model="grok-4",  # grok-3 or grok-4
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )

    tools = [
        WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
        DuckDuckGoSearchRun()
    ]
    tool_map = {tool.name: tool for tool in tools}

    llm_with_tools = llm.bind_tools(tools)
    logging.info("LLM initialized with tools.")

    messages = [HumanMessage(content=prompt)]
    max_iterations = 8
    final_content = ""

    for iteration in range(max_iterations):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            # Model returned final answer (no more tool use requested)
            final_content = response.content or ""
            logging.info(f"Final answer received (iteration {iteration}).")
            break

        # Execute any requested tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id", "")

            if tool_name in tool_map:
                logging.info(f"Calling tool '{tool_name}' with args: {tool_args}")
                try:
                    # Tools expect a dict or specific input; invoke handles it
                    result = tool_map[tool_name].invoke(tool_args)
                except Exception as e:
                    result = f"ERROR running {tool_name}: {str(e)}"
                    logging.error(result)
            else:
                result = f"Unknown tool requested: {tool_name}"
                logging.warning(result)

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call_id)
            )

    if not final_content:
        # Fallback: last AI message content
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                final_content = msg.content
                break

    logging.info(f"LLM final response length: {len(final_content)} chars")
    return final_content

def main():
    """Main function to parse args, run agent, and handle logging/history."""
    parser = argparse.ArgumentParser(
        description="linfo - Linux distro info CLI. "
                    "Run with no arguments to explore a random popular distribution (fastfetch style)."
    )
    parser.add_argument('--distro', type=str, help='Linux distribution name (e.g., Ubuntu). If omitted, a random distro is chosen.')
    parser.add_argument('--arch', type=str, help='Architecture (e.g., x86_64). Defaults to x86_64 when using random mode.')
    parser.add_argument('--level', type=str, choices=['beginner', 'intermediate', 'advanced', 'general'], help='Expertise level (omit or use "general" for a balanced response)')
    parser.add_argument('--topics', type=str, help='Comma-separated topics (e.g., features,package_management)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed logs on the console (INFO level)')
    parser.add_argument(
        '--style',
        choices=['fetch', 'markdown'],
        default=None,
        help='Output style: "fetch" for neofetch/fastfetch-style (ASCII + facts + download), '
             '"markdown" for full LLM panel. Defaults to fetch for random runs, markdown otherwise.',
    )
    parser.add_argument(
        '--brief',
        action='store_true',
        help='Show only the compact fastfetch-style view (logo + key facts + download for known distros; '
             'for others: small "Brief:" header + concise LLM info). Skips the full in-depth LLM panel. '
             'Implies --style fetch.',
    )
    args = parser.parse_args()

    # --- Random mode when no distro is provided ---
    random_mode = False
    if not args.distro:
        import random
        random_mode = True
        distro, arch = random.choice(RANDOM_DISTROS)
        args.distro = distro
        args.arch = arch or "x86_64"
        if not args.level:
            args.level = "general"

    # Default arch if user gave only --distro
    if args.distro and not args.arch:
        args.arch = "x86_64"

    # Set up logging *after* we know the verbose flag
    setup_logging(verbose=args.verbose)

    try:
        validate_inputs(args)
        history = load_history()
        logging.info(f"Loaded {len(history)} past queries.")

        # API key is obtained securely via _get_api_key() inside run_agent
        # (never stored in variables that could leak to history/logs)

        # Friendly message when we picked a random distro
        if random_mode:
            hint = "" if args.verbose else "\n    (use --verbose to see internal logs)"
            random_msg = Text.assemble(
                ("🎲  No arguments given — randomly exploring ", "bold yellow"),
                (args.distro, "bold cyan"),
                (f" ({args.arch})", "dim"),
                (hint, "dim italic"),
            )
            console.print(Panel(random_msg, border_style="yellow", padding=(0, 1)))
            console.print()

        brief = args.brief
        prompt = build_prompt(args, brief=brief)

        # Run the agent with a nice spinner for better UX
        with console.status(
            f"[bold cyan]Querying {args.distro} ({args.arch})...[/bold cyan]",
            spinner="dots",
            spinner_style="cyan",
        ):
            response = run_agent(prompt)

        # Determine effective style: --brief forces fetch; --style overrides; random defaults to fetch
        effective_style = args.style
        if brief:
            effective_style = "fetch"
        if effective_style is None:
            effective_style = "fetch" if random_mode else "markdown"

        # Build value objects (dataclasses per request)
        distro_obj = Distro.from_args(args)
        renderer = DistroRenderer(style=effective_style, brief=brief)

        # Use the renderer (it handles fetch vs markdown + brief truncation of full panel)
        renderer.render(distro_obj, response)

        new_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'args': vars(args),
            'response': response
        }
        save_history(history, new_entry)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        error_panel = Panel(
            Text(str(e), style="bold red"),
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)


if __name__ == "__main__":
    main()
