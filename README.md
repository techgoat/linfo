# linfo (2026)

[![Built with Grok Build](https://img.shields.io/badge/Built%20with-Grok%20Build-000000?style=for-the-badge)](https://x.ai)
[![CI](https://github.com/techgoat/linfo/actions/workflows/ci.yml/badge.svg)](https://github.com/techgoat/linfo/actions/workflows/ci.yml)

`linfo` is a small agentic Python CLI that uses Grok (via xAI) + Wikipedia/DuckDuckGo tools to give tailored, up-to-date information about any Linux distribution and architecture.

It can render in **fastfetch/neofetch style** (ASCII logo + key facts + direct download link), rich Markdown, or **JSON** for scripts. An **`--embedded`** profile targets IoT/appliance/build-system concerns.

**Author:** Roy Jensen ([0009-0001-2601-8028](https://orcid.org/0009-0001-2601-8028)) — [g04t@t3chg04t.wtf](mailto:g04t@t3chg04t.wtf)

**Repository:** [github.com/techgoat/linfo](https://github.com/techgoat/linfo)

## Current Features
- Clean, readable output powered by **Rich** (Markdown panels or fastfetch-style columns)
- `--style fetch|markdown` to choose output format
- `--brief` for compact fastfetch view only (logo + facts + download when the distro is in the built-in database; otherwise a small "Brief:" header + concise LLM output, no long LLM panel)
- `--embedded` for embedded/IoT focus (build system, footprint, init, updates, targets + tailored prompts)
- `--json` for machine-readable stdout (scripting / pipelines)
- `--model` / `XAI_MODEL` to select the xAI model (default `grok-4`)
- Random mode (no args) defaults to attractive fastfetch-style with ASCII; with `--embedded`, picks from an embedded-oriented pool
- **neofetch / fastfetch style**: ASCII art logo + key facts + prominent **official download link**
- Reliable official download links (curated per distro)
- Agentic tool use (the model can search the web + Wikipedia in a loop)
- Query history saved to `logs/query_history.json`
- Full transaction logging to `logs/transaction_log.txt` (logs/ subfolder is created automatically)
- Support for expertise level and custom topics
- Modular `src/linfo/` package (`data`, `models`, `renderer`, `agent`, `secrets`, `history`, `output`)
- Design follows Arjan Codes principles (SRP, separation of concerns, small dataclasses) + OWASP secrets + agentic security practices
- Includes `tests/` with pytest (run via `uv run --extra test pytest`)
- Full documentation site powered by **MkDocs + Material + mkdocstrings** (`uv run --extra docs mkdocs serve`)
- `examples/` with CLI and programmatic use-cases
- Professional release hygiene: `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, issue/PR templates, GitHub Actions CI
- Future ideas tracked in `ROADMAP.md`

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
uv run linfo --help
# or
uv run python -m linfo --help
# root main.py is a thin shim to the same entrypoint:
uv run python main.py --help
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

# Brief / compact mode
linfo --brief
linfo --distro Arch --brief
linfo --distro "Linux Mint" --style fetch --brief

# Embedded / IoT profile
linfo --embedded
linfo --distro OpenWrt --embedded --brief
linfo --distro "Yocto Project" --embedded --level advanced

# Machine-readable JSON (great for scripts)
linfo --distro Ubuntu --brief --json
linfo --distro Alpine --embedded --json | jq .static_data.build_system

# Works for any distro (even ones not in the built-in databases)
linfo --distro "Parrot Security" --brief

# With verbose logging
linfo -v
linfo --distro Ubuntu --verbose
```

**Requirements:**
- `XAI_API_KEY` in `.env` (or environment)
- Python 3.12+
- `uv` (recommended)

**Documentation**: Full site at `docs/` (MkDocs). Build locally with `uv run --extra docs mkdocs serve` after installing the docs extra. See `docs/architecture.md` for design details and guardrails.

**Versioning**: Follows Semantic Versioning (SemVer) + PEP 440. See `CHANGELOG.md`. Current: see `pyproject.toml` or `python -c "import linfo; print(linfo.__version__)"`.

## License

This project is released under the [MIT License](LICENSE).

## Acknowledgements

This project was developed with significant assistance from **Grok Build** by xAI.

## Citation

If you use or reference this software in academic work, please cite it using the metadata in [CITATION.cff](CITATION.cff).

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

(Research findings and early design notes from the original development thread are retained
in git history; the live product surface is documented above and in `docs/`.)
