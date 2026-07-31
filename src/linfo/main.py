#!/usr/bin/env python3
"""
src/linfo/main.py

linfo - Linux distro info CLI (fastfetch-style + rich LLM details).

Thin orchestration layer: argparse, random mode, agent call, render / JSON.

Author: Roy Jensen <g04t@t3chg04t.wtf>
ORCID: https://orcid.org/0009-0001-2601-8028

Design notes (Arjan Codes inspired):
- Single Responsibility: data, models, renderer, agent, secrets, history, output
  live in focused modules; main() only wires them together.
- Security (OWASP Secrets + LLM Agentic): API keys never hardcoded, never logged,
  fetched just-in-time via get_api_key. Tools are read-only. Limited agency.
- Project uses the recommended `src/` layout.

MIT License — see LICENSE file for details.
"""

from __future__ import annotations

import argparse
import logging
import time

from dotenv import load_dotenv
from rich.panel import Panel
from rich.text import Text

# Re-exports for backward compatibility (tests, examples, docs)
from linfo.agent import build_prompt, run_agent
from linfo.data import (
    DISTRO_DATA,
    EMBEDDED_DISTRO_DATA,
    RANDOM_DISTROS,
    RANDOM_EMBEDDED_DISTROS,
    get_distro_data,
    normalize_distro_name,
)
from linfo.history import (
    HISTORY_FILE,
    LOGS_DIR,
    load_history,
    save_history,
    setup_logging,
)
from linfo.models import Distro
from linfo.output import build_result_payload, emit_json
from linfo.renderer import DistroRenderer, console
from linfo.secrets import get_api_key, _get_api_key  # noqa: F401

load_dotenv()


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate CLI arguments (level only — distro/arch are guaranteed by main()).

    Args:
        args: Parsed arguments.

    Raises:
        ValueError: If validation fails.
    """
    if args.level and args.level not in [
        "beginner",
        "intermediate",
        "advanced",
        "general",
    ]:
        raise ValueError(
            "Expertise level must be one of: beginner, intermediate, advanced "
            "(or omit for general)."
        )
    logging.info("Inputs validated successfully.")


def main() -> None:
    """Main function to parse args, run agent, and handle logging/history."""
    parser = argparse.ArgumentParser(
        description=(
            "linfo - Linux distro info CLI. "
            "Run with no arguments to explore a random popular distribution "
            "(fastfetch style)."
        )
    )
    parser.add_argument(
        "--distro",
        type=str,
        help="Linux distribution name (e.g., Ubuntu). If omitted, a random distro is chosen.",
    )
    parser.add_argument(
        "--arch",
        type=str,
        help="Architecture (e.g., x86_64). Defaults to x86_64 when using random mode.",
    )
    parser.add_argument(
        "--level",
        type=str,
        choices=["beginner", "intermediate", "advanced", "general"],
        help='Expertise level (omit or use "general" for a balanced response)',
    )
    parser.add_argument(
        "--topics",
        type=str,
        help="Comma-separated topics (e.g., features,package_management)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed logs on the console (INFO level)",
    )
    parser.add_argument(
        "--style",
        choices=["fetch", "markdown"],
        default=None,
        help=(
            'Output style: "fetch" for neofetch/fastfetch-style '
            '(ASCII + facts + download), "markdown" for full LLM panel. '
            "Defaults to fetch for random runs, markdown otherwise."
        ),
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help=(
            "Show only the compact fastfetch-style view (logo + key facts + download "
            'for known distros; for others: small "Brief:" header + concise LLM info). '
            "Skips the full in-depth LLM panel. Implies --style fetch."
        ),
    )
    parser.add_argument(
        "--embedded",
        action="store_true",
        help=(
            "Embedded/IoT focus: prefer embedded static facts (build system, footprint, "
            "init, updates, targets), tailor the LLM prompt for appliance/BSP concerns, "
            "and use an embedded-oriented random pool when no --distro is given."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Emit machine-readable JSON on stdout instead of Rich panels "
            "(still runs the agent; use for scripting). Decorative banners are suppressed."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="xAI model id (default: env XAI_MODEL or grok-4).",
    )
    args = parser.parse_args()

    # --- Random mode when no distro is provided ---
    random_mode = False
    if not args.distro:
        import random

        random_mode = True
        pool = RANDOM_EMBEDDED_DISTROS if args.embedded else RANDOM_DISTROS
        distro, arch = random.choice(pool)
        args.distro = distro
        args.arch = arch or "x86_64"
        if not args.level:
            args.level = "general"

    # Default arch if user gave only --distro
    if args.distro and not args.arch:
        args.arch = "x86_64"

    setup_logging(verbose=args.verbose)

    try:
        validate_inputs(args)
        history = load_history()
        logging.info(f"Loaded {len(history)} past queries.")

        if random_mode and not args.json:
            hint = "" if args.verbose else "\n    (use --verbose to see internal logs)"
            mode_label = "embedded " if args.embedded else ""
            random_msg = Text.assemble(
                (
                    f"🎲  No arguments given — randomly exploring {mode_label}",
                    "bold yellow",
                ),
                (args.distro, "bold cyan"),
                (f" ({args.arch})", "dim"),
                (hint, "dim italic"),
            )
            console.print(Panel(random_msg, border_style="yellow", padding=(0, 1)))
            console.print()

        brief = args.brief
        embedded = args.embedded
        prompt = build_prompt(args, brief=brief, embedded=embedded)

        if args.json:
            # Quiet path for scripts: no spinner noise on stdout
            response = run_agent(prompt, model=args.model)
        else:
            with console.status(
                f"[bold cyan]Querying {args.distro} ({args.arch})...[/bold cyan]",
                spinner="dots",
                spinner_style="cyan",
            ):
                response = run_agent(prompt, model=args.model)

        effective_style = args.style
        if brief:
            effective_style = "fetch"
        if effective_style is None:
            effective_style = "fetch" if (random_mode or embedded) else "markdown"

        distro_obj = Distro.from_args(args)

        if args.json:
            payload = build_result_payload(
                distro_obj,
                response=response,
                style=effective_style,
                brief=brief,
                embedded=embedded,
                random_mode=random_mode,
            )
            emit_json(payload)
        else:
            renderer = DistroRenderer(
                style=effective_style,
                brief=brief,
                embedded=embedded,
            )
            renderer.render(distro_obj, response)

        new_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "args": vars(args),
            "response": response,
        }
        save_history(history, new_entry)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        if args.json:
            import json
            import sys

            json.dump({"error": str(e)}, sys.stderr, indent=2)
            sys.stderr.write("\n")
            raise SystemExit(1) from e
        error_panel = Panel(
            Text(str(e), style="bold red"),
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)


if __name__ == "__main__":
    main()
