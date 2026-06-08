# linfo (2026)

[![Built with Grok Build](https://img.shields.io/badge/Built%20with-Grok%20Build-000000?style=for-the-badge)](https://x.ai)

`linfo` is a small agentic Python CLI that uses Grok (via xAI) + Wikipedia/DuckDuckGo tools to give tailored, up-to-date information about any Linux distribution and architecture.

It can render in **fastfetch/neofetch style** (ASCII logo + key facts + direct download link) or rich Markdown.

**Author:** Roy Jensen ([0009-0001-2601-8028](https://orcid.org/0009-0001-2601-8028)) — [g04t@t3chg04t.wtf](mailto:g04t@t3chg04t.wtf)

## Current Features
- Clean, readable output powered by **Rich** (Markdown panels or fastfetch-style columns)
- `--style fetch|markdown` to choose output format
- `--brief` for compact fastfetch view only (logo + facts + download when the distro is in the built-in database; otherwise a small "Brief:" header + concise LLM output, no long LLM panel)
- Random mode (no args) defaults to attractive fastfetch-style with ASCII
- **neofetch / fastfetch style**: ASCII art logo + key facts (PM, desktop, release model) + prominent **official download link**
- Reliable official download links (curated per distro)
- Agentic tool use (the model can search the web + Wikipedia in a loop)
- Query history saved to `logs/query_history.json`
- Full transaction logging to `logs/transaction_log.txt` (logs/ subfolder is created automatically)
- Support for expertise level and custom topics
- Design follows Arjan Codes principles (SRP, separation of concerns, small dataclasses for Distro + Renderer, and the recommended `src/` project layout) + OWASP secrets + agentic security practices (centralized key handling, limited tool agency, no secret leakage)
- Includes `tests/` with pytest cases (run via `uv run --extra test pytest`) covering input validation, Distro/DistroRenderer, --brief/--style paths, logging/history to subfolder, etc.
- Full documentation site powered by **MkDocs + Material + mkdocstrings** (in `docs/`, including architecture overview and auto-generated API reference). Run `uv run --extra docs mkdocs serve`.
- `examples/` with CLI and programmatic use-cases.
- Professional release hygiene: `CHANGELOG.md` (Keep a Changelog + SemVer), `CODE_OF_CONDUCT.md` (Contributor Covenant), `.github/ISSUE_TEMPLATE/` and `PULL_REQUEST_TEMPLATE.md`.
- Project-specific AI guardrails in `.grok/AGENTS.md` and `.grok/skills/linfo/SKILL.md` (Arjan Codes + OWASP; auto-activated in the tree).
- Future ideas are tracked publicly in `ROADMAP.md`, with a personal scratchpad in the `.future/` directory.

## Installation as a uv tool (recommended)

```bash
# From inside the project directory (after you have the source)
uv tool install .

# Now the `linfo` command is available globally (managed by uv)
linfo --help
linfo   # random distro, fastfetch style by default
```

After `uv tool install .` you get the `linfo` command in your PATH (uv tools bin dir).

For development / without global install:

```bash
# Inside the project dir
uv run linfo                 # uses the project entry point
# or fall back to
uv run python linfo.py --help
```

To reinstall after changes:

```bash
uv tool install --force .
```

## Usage

```bash
# Random distro (defaults to nice fastfetch view + in-depth)
linfo

# Explicit distro, full markdown panel (classic behavior)
linfo --distro Debian --arch x86_64 --level beginner

# Force fastfetch style (even for explicit)
linfo --distro Fedora --style fetch

# Brief / compact mode (logo + facts + download only for known distros; for others a compact summary header + concise LLM info, no large "In-Depth" panel)
linfo --brief
linfo --distro Arch --brief
linfo --distro "Linux Mint" --style fetch --brief

# Works for any distro (even ones not in the built-in fastfetch database)
linfo --distro "Parrot Security" --brief
linfo --distro "Parrot Security" --style fetch  # same as brief for unknown distros in terms of avoiding full panel

# With verbose logging
linfo -v
linfo --distro Ubuntu --verbose
```

**New in this version:**
- App is now installed as the `linfo` command via `uv tool install .`
- `--style fetch|markdown` flag for full control of output format.
- `--brief` flag for the compact fastfetch-style only (perfect for quick lookup; gracefully handles arbitrary distros with a compact summary).
- Random (no args) still defaults to the attractive fastfetch display.
- Official download links always prominent.
- Uses small `Distro` and `DistroRenderer` dataclasses internally.
- By default the terminal stays clean — detailed logs only appear when you pass `--verbose` / `-v`. Everything is still written to `logs/transaction_log.txt`.

The output appears in a nicely formatted bordered panel (or fastfetch-style columns) with proper headings, lists, and code formatting. Download links are always easy to find.

**Requirements:**
- `XAI_API_KEY` in `.env` (or environment)
- Python 3.14+
- `uv` (the uv tool manager handles installation of linfo and its deps)

**Documentation**: Full site at `docs/` (MkDocs). Build locally with `uv run --extra docs mkdocs serve` after installing the docs extra. See `docs/architecture.md` for design details and guardrails.

**Versioning**: Follows Semantic Versioning (SemVer) + PEP 440. See `CHANGELOG.md` for the policy and history. Current: see `pyproject.toml` or `python -c "import linfo; print(linfo.__version__)"`.

## License

This project is released under the [MIT License](LICENSE).

## Acknowledgements

This project was developed with significant assistance from **Grok Build** by xAI.

## Citation

If you use or reference this software in academic work, please cite it using the metadata in [CITATION.cff](CITATION.cff).

A preferred citation is also included in that file.

---

## Original Design Prompt (for context)

Grok Prompt:
I want to research and perhaps design a python app that operates at the CLI, and provides 
basic information about targeted Linux distributions. CLI arguments would at least include 
‘distribution name’ and ‘architecture’ but might also include ‘expertise 
level(beginner, intermediate, advanced)’, ‘features’, ‘package management’, etc. 
I would want this to be an agentic ai solution woven together with Python for use input 
validation and functional logging to record a history of past queries and a transaction 
log of the app, and of course doc-strings on all functions. If such a development 
is already available I would like to know.

Research Findings

After searching across web sources, GitHub repositories, and related queries, I couldn't 
find an existing Python CLI app that exactly matches your description—one that takes 
arguments like distribution name, architecture, expertise level, and specific topics 
(e.g., features, package management) to provide targeted information on Linux distributions 
using an agentic AI approach.

There are related tools and packages:

-   The distro PyPI package (and similar libraries) focuses on detecting and providing info 
    about the current running Linux distribution (e.g., ID, version, codename), but it doesn't 
    query or provide details on arbitrary distributions.
-   Tools like neofetch or screenfetch display system info including the current distro in 
    a visually appealing way, but again, only for the running system.
-   DistroWatch.com is a comprehensive website for Linux distro info, and there's a 
    GitHub script (py_versions_and_distros.py) that scrapes it to check Python versions 
    across distros, but it's not a full CLI app for general queries.
-   General CLI tools for system info (e.g., hostnamectl, uname, lsb_release) are limited 
    to the current environment.
-   No prominent open-source project combines AI agents with Python for dynamic, 
    parameterized queries on distros, including logging and history as specified.

Since nothing fits perfectly, I'll proceed with a design and implementation outline. 
This will be a standalone Python app using LangChain for the agentic AI component 
(to enable reasoning and tool usage for fetching accurate, up-to-date info). The AI agent 
will use tools like Wikipedia and web search to gather details, ensuring the response 
is tailored to your inputs.

Design Overview

-   CLI Interface: Use argparse for handling arguments. Required: distro (e.g., "Ubuntu"), arch 
    (e.g., "x86_64"). Optional: level (beginner/intermediate/advanced), topics (comma-separated 
    list like "features,package_management").
-   Input Validation: Check required args, validate level against choices, 
    ensure topics are split correctly.
-   Agentic AI: Use LangChain to create an agent with an LLM (I'll use Groq's API for 
    speed; you can swap with xAI's Grok API if available—it's compatible via OpenAI-style 
    clients). The agent uses tools (Wikipedia for structured info, DuckDuckGo for web searches) 
    to reason and fetch distro-specific details.
-   Logging: Use Python's logging module for a transaction log (app actions, errors). 
    Store query history in a JSON file.
-   Docstrings: Included on all functions.
-   Structure:
    -   Main script: distro_info.py
    -   Runs as `linfo` (after `uv tool install .`) or `uv run linfo` (random distro) or with explicit `--distro` / `--arch` flags. Use `-v`/`--verbose` for full logs. New flags: --style, --brief.
    -   Output: Prints tailored info; logs everything.

-   Dependencies: Managed with `uv`. See `pyproject.toml` (includes langchain, langchain-openai, rich, duckduckgo-search, wikipedia, etc.). Requires `XAI_API_KEY`.
-   Agent Behavior: The agent receives a prompt based on args and uses tools to compile 
    info (e.g., search for distro features, check architecture support). This makes it 
    "agentic" by allowing multi-step reasoning.
-   Limitations: Relies on API keys for LLM. For offline use, swap to a local LLM like Ollama.
-   Extensibility: Add more tools (e.g., browse DistroWatch) via LangChain.

Sample Implementation

Here's the full Python code for distro_info.py. Save it to a file and run it. I've included 
comments for clarity.
