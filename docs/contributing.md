# Contributing

See the root `CONTRIBUTING.md` and `README.md` (at project root) for general guidelines.

## Specific to linfo

- All changes must respect the **Project Design & Security Guardrails** (see `.grok/AGENTS.md`): Arjan Codes' Design Guide + OWASP.
- Add tests in `tests/`.
- Update `CHANGELOG.md` (Keep a Changelog format) and version per SemVer.
- For user-visible changes, consider adding to `examples/`.
- Documentation lives in `docs/` (MkDocs). Run with `uv run --extra docs mkdocs serve`.
- New distros: extend `DISTRO_DATA` + `RANDOM_DISTROS` in `src/linfo/main.py`.
- New output styles or flags: update `DistroRenderer`, parser, prompt logic if needed, tests, docs.

Run the test suite before opening a PR:

```bash
uv run --extra test pytest
```

Build docs locally to verify mkdocstrings etc.

Thank you for helping keep linfo clean, secure, and useful!
