# linfo

`linfo` is a modern, agentic command-line tool for retrieving tailored, up-to-date information about Linux distributions and architectures.

It combines the power of Grok (via xAI) + Wikipedia and web search tools with beautiful terminal output inspired by **fastfetch** / **neofetch**.

## Key Features

- **Fastfetch-style output** (`--style fetch` or default for random): ASCII art logo + key facts (package manager, desktop, release model) + prominent official download link.
- **Rich Markdown mode** (`--style markdown`): Detailed, LLM-generated narrative tailored to expertise level and topics.
- **`--brief`**: Compact view only (logo + facts + download for known distros; small "Brief:" header + concise LLM summary for others). No long panels.
- Random mode (run with no arguments) picks from curated popular distros and defaults to attractive fetch style.
- Support for **any** distro name (e.g. `linfo --distro "Parrot Security" --brief`).
- Secure by design: API keys never logged or leaked; tools are strictly read-only; LLM output is display-only.
- Follows **Arjan Codes' Software Design Guide** (SRP, small dataclasses `Distro` + `DistroRenderer`, src/ layout) and **OWASP** security guardrails for secrets and LLM/agentic apps.
- Full test coverage, MkDocs documentation, examples, and CHANGELOG.

## Quick Start

```bash
# Install as uv tool (recommended)
uv tool install .

# Explore a random distro (fastfetch style + details)
linfo

# Specific distro, brief mode
linfo --distro Ubuntu --brief

# Force markdown style for a custom distro
linfo --distro "Parrot Security" --style markdown --level intermediate
```

See [Usage](usage.md) and the `examples/` directory (at project root) for more.

## Project Principles

This project strictly follows:

- Arjan Codes' Design Guide (see `.grok/AGENTS.md`).
- OWASP Secrets Management and Top 10 for LLM/Agentic Applications.

All contributions and AI-assisted changes must respect these guardrails.

## Documentation

- [Architecture Overview](architecture.md)
- [API Reference](api.md) (auto-generated via mkdocstrings)
- [Usage & Examples](usage.md)
- [Contributing](contributing.md) (includes tests, docs, versioning)

## Versioning

We follow [Semantic Versioning (SemVer)](https://semver.org/) with [PEP 440](https://peps.python.org/pep-0440/) compatibility for Python packaging. See the root `CHANGELOG.md` for details.

Current version: see `pyproject.toml` or `import linfo; print(linfo.__version__)`.

## License

MIT. See the LICENSE file at the project root.

Built with assistance from Grok Build (xAI).
