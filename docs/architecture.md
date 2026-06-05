# Architecture Overview

`linfo` follows a clean, maintainable structure inspired by **Arjan Codes' Software Design Guide** (SRP, small focused classes, dependency inversion, readability) and uses the recommended `src/` layout.

## High-Level Design

- **Single Responsibility**: 
  - `Distro` dataclass: Represents a query target + its static data (from `DISTRO_DATA`).
  - `DistroRenderer` dataclass: Encapsulates all output logic (`--style`, `--brief`, Rich rendering of fetch vs. markdown).
  - `run_agent`: Pure agentic LLM + tool-calling loop (manual, no LangGraph).
  - `main()`: Orchestration, arg parsing, logging setup, history, random mode.
  - Data lookup (`get_distro_data`, normalize) and secure secrets (`_get_api_key`) are isolated.

- **Guardrails Enforcement**:
  - **Arjan Codes**: Dataclasses for models, renderer owns presentation, no god objects, clear boundaries. src/ layout prevents import issues.
  - **OWASP**:
    - Secrets: Never hardcoded, fetched JIT, never in prompts/history/logs, fail-closed with validation.
    - Agentic/LLM: Tools read-only (no shell, no writes). LLM output is **only displayed** (never executed or fed back unsafely). `--brief` uses concise prompts + early return to limit verbosity/agency. Input validation on levels/topics.

- **Output Modes** (controlled by `DistroRenderer`):
  - `fetch`: Side-by-side Rich Panels (ASCII logo + "System Info" facts including download). Used by default for random, or `--style fetch`.
  - `markdown`: Full LLM narrative in a titled Panel + optional download footer.
  - `brief=True` (or `--brief`): Forces fetch (if data) + **early return** (no in-depth panel). For unknown distros: small "Brief:" header + concise LLM summary (no large panel).
  - Random mode auto-defaults to fetch + shows a friendly banner.

- **Data**:
  - `DISTRO_DATA`: Curated static facts + ASCII (neofetch-inspired) + reliable download URLs for popular distros.
  - `RANDOM_DISTROS`: For no-arg random selection.
  - Unknown distros (e.g. "Parrot Security") still work fully via LLM + tools; brief falls back gracefully.
  - Extend `DISTRO_DATA` when adding popular distros (ASCII, pkg_manager, etc.).

- **Agent Loop** (`run_agent`):
  - Uses LangChain `ChatOpenAI` (xAI Grok-4 compatible endpoint) + `bind_tools`.
  - Manual ReAct-style loop (WikipediaQueryRun + DuckDuckGoSearchRun).
  - Max iterations guard. Tool results fed back as `ToolMessage`.
  - Never puts secrets in messages.

- **CLI & Config**:
  - `argparse` in `main()`.
  - Flags: `--distro`, `--arch`, `--level`, `--topics`, `--style`, `--brief`, `-v/--verbose`.
  - Logging: Always to `logs/transaction_log.txt`; console only on `--verbose`.
  - History: `logs/query_history.json` (full responses for audit).
  - `logs/` created automatically; gitignored except `.gitkeep`.

- **Packaging** (uv/hatchling):
  - src/ layout.
  - Console script: `linfo = "linfo.__main__:main"`.
  - Optional extras: `test`, `docs`.

- **Testing**:
  - `tests/test_linfo.py` (pytest).
  - Mocks for LLM (`run_agent`), console, file handlers.
  - Covers: input validation, dataclasses, renderer branches (brief/style/data presence), prompt variants, log dir logic, etc.
  - Run: `uv run --extra test pytest`.

- **Docs**:
  - MkDocs + Material + mkdocstrings (auto API from `src/linfo`).
  - Architecture, usage, examples.

## File Structure (Key Parts)

```
src/linfo/
  main.py          # All logic, dataclasses, agent, renderer, CLI
  __main__.py      # python -m linfo + entrypoint shim
  __init__.py      # __version__
tests/
  test_linfo.py
docs/
  (MkDocs sources + api.md via mkdocstrings)
examples/
  (runnable snippets)
logs/              # runtime only (gitignored)
.grok/             # AGENTS.md + skills/linfo/SKILL.md (local + committed instructions)
```

## Why This Design?

- Small CLI but treated professionally (per Arjan).
- Easy to extend (new distros, new styles, future adapters for other LLMs/tools).
- Secure and predictable for an LLM agent.
- Beautiful UX out of the box (fetch) while supporting power users (full markdown).

See `src/linfo/main.py` for implementation details and inline comments referencing the guardrails.

See [API Reference](api.md) for public surface.
