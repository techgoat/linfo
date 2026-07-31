# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
(with PEP 440 compatibility for Python packaging).

## [Unreleased]

## [0.6.0] - 2026-07-31

### Added
- **`--json`**: Machine-readable JSON on stdout for scripting (stable payload with name, arch, flags, static_data without ASCII blob, response).
- **`--embedded`**: Embedded/IoT profile — embedded static database (Alpine, OpenWrt, Yocto, Buildroot, BusyBox, Raspberry Pi OS Lite, balenaOS), tailored LLM prompts (build system, footprint, init, OTA), embedded-oriented fetch facts, and a dedicated random pool when no `--distro` is given.
- **`--model`**: Optional xAI model override (also respects `XAI_MODEL` env).
- **Module split** under `src/linfo/`: `data`, `models`, `renderer`, `agent`, `secrets`, `history`, `output`, thin `main` orchestration (Arjan SRP).
- **GitHub Actions CI** (`.github/workflows/ci.yml`) running pytest on Python 3.12–3.14.
- Minimal **pre-commit** config (trailing whitespace, YAML, large files).

### Fixed
- Restore **`ddgs`** dependency required by LangChain's `DuckDuckGoSearchRun` (without it: "Please install it with pip install -U ddgs"). Prefer `ddgs` over the older `duckduckgo-search` package name.

### Changed
- **Repo hygiene**: `site/` and `.idea/` no longer tracked; gitignored. Root `main.py` is a real shim to `linfo.main`. CHANGELOG/README/mkdocs URLs point at `https://github.com/techgoat/linfo`.
- **Dependencies**: Dropped unused `langchain-groq`. Web search tool depends on **`ddgs`**. `requires-python` relaxed to `>=3.12` for broader installability.
- Public package re-exports from `linfo` (`Distro`, `DistroRenderer`, helpers).
- Version bumped to **0.6.0**.

### Documentation
- README, usage, architecture, examples, ROADMAP, CITATION.cff updated for `--json` / `--embedded` and new module layout.

## [0.5.0] - 2025-06-05

### Added
- **Project documentation infrastructure**: Full MkDocs + Material setup in `docs/` (index, architecture overview, API reference via mkdocstrings, usage, contributing). `mkdocs.yml` at root. New `docs` optional extra in pyproject.toml. Run with `uv run --extra docs mkdocs serve`.
- **examples/** folder with practical use-cases:
  - `cli-examples.sh`: Common command invocations (random, --brief, --style, arbitrary distros like Parrot Security, verbose).
  - `programmatic.py`: Direct use of `Distro` / `DistroRenderer` dataclasses.
- **CHANGELOG.md** (this file) initialized with full chat history.
- **.github/ISSUE_TEMPLATE/** (bug_report.md, feature_request.md, config.yml) and **PULL_REQUEST_TEMPLATE.md** for standardized contributions.
- **CODE_OF_CONDUCT.md** populated with Contributor Covenant v2.1.
- Enhanced `.grok/` project-specific instructions:
  - `.grok/AGENTS.md`: High-level mandatory guardrails (Arjan Codes Design Guide + OWASP LLM/Agentic/Secrets).
  - `.grok/skills/linfo/SKILL.md`: Detailed development skill (commands, patterns, guardrails activation, MkDocs, testing, etc.).
  - Updated `.gitignore` to ignore `.grok/` by default while allowing committed instruction files (`.grok/AGENTS.md`, `.grok/skills/**/SKILL.md`).
- Added "Parrot Security" (and a few others) to `DISTRO_DATA` + `RANDOM_DISTROS` for better out-of-box experience with `--brief` on real-world distros.
- Refined `--brief` behavior and prompt generation for arbitrary/unknown distros (small "Brief:" header + concise LLM output instead of full In-Depth panel). Prompt now requests "concise summary" when `brief=True`.
- Version bumped to 0.5.0 (see Versioning section below).

### Changed
- **Versioning policy**: Now explicitly follows Semantic Versioning (SemVer 2.0.0) + PEP 440. Documented in docs, AGENTS.md, and this changelog. All future bumps must sync with CHANGELOG entries.
- Logs/history paths and references updated throughout (now consistently under `logs/`).
- README and docs updated to reflect all new folders, commands, and guardrails terminology ("Project Design & Security Guardrails").
- Internal: `build_prompt` now accepts `brief: bool` to produce shorter LLM output for `--brief` mode. Renderer logic strengthened for brief paths regardless of static data presence.

### Documentation
- Architectural overview written (references Arjan SRP, OWASP, dataclasses, renderer, agent loop, guardrails).
- API reference page for mkdocstrings.
- Usage page with examples.
- Contributing page specific to linfo + guardrails.

## [0.4.0] - Previous (refinements from earlier in thread)

### Added
- `tests/` folder + comprehensive pytest suite (`tests/test_linfo.py`, 16+ tests). Covers input validation, `Distro`/`DistroRenderer` dataclasses, `--brief`/`--style` branches, prompt variants (brief vs normal), log subdir logic, etc. Mocks for LLM and console. Run via `uv run --extra test pytest`.
- `logs/` subfolder support: `transaction_log.txt` and `query_history.json` now live in `logs/` (auto-created). Updated code, .gitignore, pyproject hatch config, tests, README.
- Full support for arbitrary distros with `--brief` / `--style fetch` (graceful fallback when no static `DISTRO_DATA` entry).
- `Distro` and `DistroRenderer` dataclasses (small, focused, per Arjan SRP recommendation). Refactored rendering and main() to use them.
- `--style fetch|markdown` flag (user control over output format; random defaults to fetch).
- `--brief` flag (forces compact view + suppresses long LLM panels).
- Project renamed to `linfo` (app name + command). `uv tool install .` support with proper console script (`linfo = "linfo.__main__:main"`).
- `src/linfo/` layout (Arjan-recommended for clean packaging and to avoid import shadowing). Updated pyproject (hatch sources/packages, entrypoint to `__main__`).
- Proper `uv tool` / editable dev workflows documented.
- `.grok/AGENTS.md` and `.grok/skills/linfo/SKILL.md` (project guardrails for Arjan Codes + OWASP; activated when working in the tree).
- Many internal cleanups: centralized secure `_get_api_key()`, better prompt for practical info, back-compat shims removed, etc.

### Changed
- Version bumped progressively (0.1.0 → 0.4.0) reflecting rename, new CLI surface, major refactors (dataclasses + renderer + src layout), tests, logs subdir, and guardrails formalization.
- Output for random mode and `--brief` now consistently compact where intended.
- All references (README, code docs, help text) updated from old "2026-linux-info" / `linux-info-v1.py` to `linfo`.
- Logging/history paths and "log file in subfolder" behavior finalized.

## [0.3.0] and earlier (core features from initial development)

- Initial agentic CLI with LangChain + xAI Grok, Wikipedia/DuckDuckGo tools, manual tool-calling loop.
- Rich output (panels, Markdown, status spinners, colored titles).
- Random distro mode (no args) with curated list.
- `--verbose` for console logs (otherwise silent; always to file).
- Input validation, history (`query_history.json`), transaction logging.
- Distro data + ASCII (neofetch-inspired), official download links (initially for curated list).
- Security improvements (centralized secrets, never in history/prompts).
- Design alignment with Arjan Codes (SRP comments, small functions) and OWASP (secrets, limited agency).
- Various fixes (tool calling loop, empty responses, ddgs import issues, etc.).
- Packaging as installable project (pyproject, uv support).

## Versioning Recommendations & Community Standard

**We follow Semantic Versioning (SemVer 2.0.0)**: https://semver.org/

- **MAJOR** (e.g. 1.0.0): Incompatible / breaking changes (public API, behavior that would surprise existing users, major refactors that change CLI contract).
- **MINOR** (e.g. 0.6.0): Backwards-compatible new features (new flags like --style/--brief/--json/--embedded, new documentation systems, new examples, added distros to DB, new guardrails files).
- **PATCH** (e.g. 0.4.1): Backwards-compatible bug fixes and small improvements.

**Python Packaging Note (PEP 440)**: We use `major.minor.patch` compatible with PEP 440. Pre-releases use `0.5.0a1`, `0.5.0rc1`, etc. (no hyphens in public versions).

**Pre-1.0 Policy**: While version < 1.0.0, the project is considered unstable. Minor versions may contain breaking changes. We aim for stability around 1.0.

**How we bump**:
1. Update `pyproject.toml` + `src/linfo/__init__.py` + `CITATION.cff`.
2. Add clear entry to top of `CHANGELOG.md` under a new `## [X.Y.Z] - YYYY-MM-DD` section (categorized Added/Changed/Fixed/etc.).
3. Tag the release in git.
4. (Future) Consider automation via `python-semantic-release` + Conventional Commits.

See full discussion in the research section of development notes and `.grok/AGENTS.md`.

## Links

[Unreleased]: https://github.com/techgoat/linfo/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/techgoat/linfo/releases/tag/v0.6.0
[0.5.0]: https://github.com/techgoat/linfo/releases/tag/v0.5.0

---

*This changelog was initialized and populated based on the full conversation history of the linfo project.*
