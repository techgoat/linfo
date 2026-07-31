#!/usr/bin/env python3
"""
src/linfo/main.py

linfo - Linux distro info CLI (fastfetch-style + rich LLM details).

Thin orchestration layer: argparse, random mode, offline/agent paths, render / JSON.

Author: Roy Jensen <g04t@t3chg04t.wtf>
ORCID: https://orcid.org/0009-0001-2601-8028

Design notes (Arjan Codes inspired):
- Single Responsibility: data, models, renderer, agent, providers, secrets,
  history, output, offline live in focused modules; main() only wires them.
- Security (OWASP Secrets + LLM Agentic): API keys never hardcoded, never logged,
  resolved via providers key chain. Tools are read-only. Limited agency.
- Offline / non-agentic mode needs no key and never calls the LLM.
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
from linfo.offline import build_static_summary, offline_missing_data_message
from linfo.output import build_result_payload, emit_json
from linfo.providers import (
    DEFAULT_PROVIDER,
    has_usable_credentials,
    list_provider_ids,
    provider_help_text,
    resolve_llm_config,
    resolve_provider_id,
)
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
    """Main function to parse args, run agent or offline path, handle logging/history."""
    parser = argparse.ArgumentParser(
        description=(
            "linfo - Linux distro info CLI. "
            "Run with no arguments to explore a random popular distribution "
            "(fastfetch style). Default LLM provider is xAI; use --offline "
            "for static-only mode without an API key."
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
            '(ASCII + facts + download), "markdown" for full LLM/static panel. '
            "Defaults to fetch for random/offline/embedded, markdown otherwise."
        ),
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help=(
            "Show only the compact fastfetch-style view (logo + key facts + download "
            'for known distros; for others: small "Brief:" header + concise info). '
            "Skips the full in-depth panel. Implies --style fetch."
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
            "Emit machine-readable JSON on stdout instead of Rich panels. "
            "Decorative banners are suppressed."
        ),
    )
    parser.add_argument(
        "--offline",
        "--non-agentic",
        action="store_true",
        dest="offline",
        help=(
            "Static-only mode: no LLM, no API key, no web tools. Uses curated "
            "DISTRO_DATA / EMBEDDED_DISTRO_DATA. Alias: --non-agentic."
        ),
    )
    parser.add_argument(
        "--force-agentic",
        action="store_true",
        help=(
            "Require agentic LLM mode; do not auto-fall back to offline when "
            "no API key is configured. Errors if credentials are missing."
        ),
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=list_provider_ids(),
        help=provider_help_text() + f" Env: LINFO_LLM_PROVIDER (default {DEFAULT_PROVIDER}).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=(
            "Model id override (default: provider-specific env or built-in default; "
            "xAI uses XAI_MODEL / grok-4)."
        ),
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="OpenAI-compatible API base URL override (or env LINFO_LLM_BASE_URL).",
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
        if args.offline and args.force_agentic:
            raise ValueError("Cannot combine --offline / --non-agentic with --force-agentic.")

        history = load_history()
        logging.info(f"Loaded {len(history)} past queries.")

        provider_id = resolve_provider_id(args.provider)
        auto_offline = False
        offline = bool(args.offline)

        if not offline and not args.force_agentic:
            if not has_usable_credentials(provider_id, base_url=args.base_url):
                offline = True
                auto_offline = True
                logging.info(
                    "No usable credentials for provider=%s; auto offline mode.",
                    provider_id,
                )

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

        if auto_offline and not args.json:
            notice = Text.assemble(
                ("Offline mode: ", "bold yellow"),
                (
                    f"no API key for provider '{provider_id}'. "
                    "Using curated static data only (no LLM). "
                    "Set a provider key (e.g. XAI_API_KEY) or pass --force-agentic to require LLM.",
                    "dim",
                ),
            )
            console.print(Panel(notice, border_style="yellow", padding=(0, 1)))
            console.print()
        elif offline and args.offline and not args.json and not auto_offline:
            notice = Text.assemble(
                ("Offline / non-agentic: ", "bold yellow"),
                ("static curated data only — no LLM, no API key required.", "dim"),
            )
            console.print(Panel(notice, border_style="dim yellow", padding=(0, 1)))
            console.print()

        brief = args.brief
        embedded = args.embedded
        distro_obj = Distro.from_args(args)

        llm_cfg = None
        response: str | None = None

        if offline:
            if not distro_obj.data:
                raise ValueError(
                    offline_missing_data_message(
                        args.distro, embedded=embedded
                    )
                )
            response = build_static_summary(distro_obj)
            # Offline defaults to compact fetch unless user forced markdown
            if brief is False and args.style is None:
                brief = True
            logging.info("Offline static summary length: %s chars", len(response or ""))
        else:
            llm_cfg = resolve_llm_config(
                provider=args.provider,
                model=args.model,
                base_url=args.base_url,
                require_key=True,
            )
            prompt = build_prompt(args, brief=brief, embedded=embedded)

            if args.json:
                response = run_agent(
                    prompt,
                    model=args.model,
                    config=llm_cfg,
                )
            else:
                with console.status(
                    f"[bold cyan]Querying {args.distro} ({args.arch}) "
                    f"via {llm_cfg.provider}/{llm_cfg.model}...[/bold cyan]",
                    spinner="dots",
                    spinner_style="cyan",
                ):
                    response = run_agent(
                        prompt,
                        model=args.model,
                        config=llm_cfg,
                    )

        effective_style = args.style
        if brief:
            effective_style = "fetch"
        if effective_style is None:
            effective_style = (
                "fetch" if (random_mode or embedded or offline) else "markdown"
            )

        resolved_provider = llm_cfg.provider if llm_cfg else (provider_id if not offline else None)
        resolved_model = llm_cfg.model if llm_cfg else None

        if args.json:
            payload = build_result_payload(
                distro_obj,
                response=response,
                style=effective_style,
                brief=brief,
                embedded=embedded,
                random_mode=random_mode,
                offline=offline,
                provider=resolved_provider if not offline else provider_id,
                model=resolved_model,
            )
            emit_json(payload)
        else:
            renderer = DistroRenderer(
                style=effective_style,
                brief=brief,
                embedded=embedded,
            )
            renderer.render(distro_obj, response)

        # History: never store secrets; offline stores static text only
        hist_args = {
            k: v
            for k, v in vars(args).items()
            if k not in ()  # placeholder; keys never in args
        }
        hist_args["offline"] = offline
        hist_args["auto_offline"] = auto_offline
        hist_args["resolved_provider"] = resolved_provider if not offline else provider_id
        if llm_cfg:
            hist_args["resolved_model"] = llm_cfg.model
            hist_args["key_source"] = llm_cfg.key_source  # name of env var only, not value

        new_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "args": hist_args,
            "response": response,
            "offline": offline,
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
