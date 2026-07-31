# Architecture Overview

`linfo` follows a clean, maintainable structure inspired by **Arjan Codes' Software Design Guide** (SRP, small focused classes, dependency inversion, readability) and uses the recommended `src/` layout.

## High-Level Design

- **Single Responsibility** (modules under `src/linfo/`):
  - `data.py`: `DISTRO_DATA`, `EMBEDDED_DISTRO_DATA`, random pools, normalize/lookup.
  - `models.py`: `Distro` dataclass (query target + static data + embedded flag).
  - `renderer.py`: `DistroRenderer` — all Rich presentation (`--style`, `--brief`, `--embedded` facts).
  - `agent.py`: `build_prompt`, `run_agent` (manual tool-calling loop; provider-aware).
  - `providers.py`: OpenAI-compatible provider registry, key chain, `LLMConfig` resolution (default **xai**).
  - `offline.py`: Static summary + offline error messages (no LLM).
  - `secrets.py`: `get_api_key` / `_get_api_key` (delegates to providers; fail-closed, never logged).
  - `history.py`: `setup_logging`, load/save history under `logs/`.
  - `output.py`: JSON payload for `--json` (includes `offline`, `provider`, `model`).
  - `main.py`: CLI orchestration only (argparse, offline/agent paths, wire modules).

- **Guardrails Enforcement**:
  - **Arjan Codes**: Dataclasses for models, renderer owns presentation, no god objects, clear boundaries. src/ layout prevents import issues.
  - **OWASP**:
    - Secrets: Never hardcoded, fetched JIT, never in prompts/history/logs, fail-closed with validation.
    - Agentic/LLM: Tools read-only (no shell, no writes). LLM output is **only displayed** (never executed). `--brief` uses concise prompts + early return. Input validation on levels.

- **Output Modes** (controlled by `DistroRenderer` / `output.emit_json`):
  - `fetch`: Side-by-side Rich Panels (ASCII logo + facts including download).
  - `markdown`: Full LLM narrative in a titled Panel + optional download footer.
  - `brief=True`: Forces compact path (fetch if data else brief summary); no in-depth panel.
  - `embedded=True`: Prefer embedded fact rows (build, footprint, init, updates, targets) and tailored prompts.
  - `--json`: Structured stdout payload via `build_result_payload` (ASCII logos omitted from JSON; `has_ascii_logo` flag instead).
  - `--offline` / `--non-agentic`: No LLM; static DB only. Auto-offline when no usable provider key (unless `--force-agentic`).
  - Random mode auto-defaults to fetch + shows a friendly banner (suppressed with `--json`).

- **Data**:
  - `DISTRO_DATA`: Curated desktop/server facts + ASCII + download URLs.
  - `EMBEDDED_DISTRO_DATA`: Embedded/IoT/build-system oriented facts.
  - `RANDOM_DISTROS` / `RANDOM_EMBEDDED_DISTROS`: No-arg selection pools.
  - Unknown distros still work fully via LLM + tools; brief falls back gracefully.

- **Providers** (`providers.py`):
  - Default provider: **xai**. Others: openai, groq, openrouter, ollama, custom.
  - Key chain per provider (e.g. `XAI_API_KEY` → `AI_API_KEY` → `LINFO_API_KEY`).
  - Env: `LINFO_LLM_PROVIDER`, `LINFO_LLM_MODEL`, `LINFO_LLM_BASE_URL`.

- **Agent Loop** (`run_agent`):
  - Uses LangChain `ChatOpenAI` (OpenAI-compatible `base_url`) + `bind_tools`.
  - Manual ReAct-style loop (WikipediaQueryRun + DuckDuckGoSearchRun).
  - Max iterations guard. Tool results fed back as `ToolMessage`.
  - Config from `resolve_llm_config` / `LLMConfig`.
  - Never puts secrets in messages.

- **CLI & Config**:
  - Flags: `--distro`, `--arch`, `--level`, `--topics`, `--style`, `--brief`, `--embedded`, `--json`, `--offline`, `--force-agentic`, `--provider`, `--model`, `--base-url`, `-v/--verbose`.
  - Logging: Always to `logs/transaction_log.txt`; console only on `--verbose`.
  - History: `logs/query_history.json`.
  - `logs/` created automatically; gitignored except `.gitkeep`.

- **Packaging** (uv/hatchling):
  - src/ layout.
  - Console script: `linfo = "linfo.__main__:main"`.
  - Optional extras: `test`, `docs`.
  - Python `>=3.12`.

- **Testing**:
  - `tests/test_linfo.py` (pytest).
  - Mocks for LLM, console, file handlers.
  - Covers validation, dataclasses, renderer branches, embedded data, JSON shape, prompts, log dir.
  - Run: `uv run --extra test pytest`.
  - CI: GitHub Actions on push/PR.

- **Docs**:
  - MkDocs + Material + mkdocstrings.
  - Build output (`site/`) is **not** committed; build locally or in Pages CI later.

## File Structure (Key Parts)

```
src/linfo/
  __init__.py      # version + public re-exports
  __main__.py      # python -m linfo
  main.py          # CLI orchestration + back-compat re-exports
  data.py          # static DBs + lookup
  models.py        # Distro
  renderer.py      # DistroRenderer + shared Console
  agent.py         # prompts + tool loop
  providers.py     # multi-provider + key chain
  offline.py       # static non-agentic path
  secrets.py       # API key (compat wrapper)
  history.py       # logging + history JSON
  output.py        # --json payload
tests/
  test_linfo.py
docs/
examples/
logs/              # runtime only (gitignored)
.github/workflows/ci.yml
```

## Why This Design?

- Small CLI but treated professionally (per Arjan).
- Easy to extend (new distros, profiles like smallbase, new output formats).
- Security boundaries stay obvious when modules are small.
