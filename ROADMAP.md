# linfo Roadmap

This document captures planned and aspirational features for future versions of **linfo**.

It is intentionally high-level and speculative. Concrete work is tracked in GitHub Issues/Milestones and documented in [CHANGELOG.md](CHANGELOG.md) under the `[Unreleased]` section when implementation begins.

**Guiding Principles for New Features**
- Must respect the Project Design & Security Guardrails (see `.grok/AGENTS.md`).
- Prefer small, focused, well-tested additions that align with the existing `Distro` + `DistroRenderer` architecture.
- New capabilities should work gracefully for both curated distros (with rich static data) and arbitrary distros (LLM-driven).
- Documentation, tests, and examples should be added alongside code changes.

## High Priority / Near-term Ideas

### `--embedded` / Embedded & IoT Focused Mode
Support for Linux distributions and build systems commonly used in embedded, IoT, and appliance scenarios.

**Motivation**
- Many users work with resource-constrained or specialized environments (routers, industrial devices, single-board computers, containers, etc.).
- These systems often use very different tooling than desktop/server distros.

**Examples of target systems**
- Yocto Project / OpenEmbedded
- Buildroot
- BusyBox-based minimal systems
- OpenWrt / LEDE
- Alpine (in embedded contexts)
- Raspberry Pi OS Lite / custom embedded images
- balenaOS, ResinOS-style appliance OSes

**Possible behaviors**
- `linfo --embedded` (or `--style embedded`)
- Different / additional facts in the fastfetch-style view:
  - Target architecture / SoC families
  - Build system (Yocto layer, Buildroot defconfig, etc.)
  - Image size / footprint
  - Init system (BusyBox, systemd, OpenRC, etc.)
  - Package / update mechanism (opkg, rpm-ostree, swupdate, etc.)
  - Common use cases (gateway, HMI, headless, etc.)
- Tailored LLM prompts that emphasize build-time vs runtime concerns, cross-compilation, licensing (for Yocto), etc.
- Possibly special handling or links to documentation for the major build systems.

**Rough implementation notes**
- Extend `DISTRO_DATA` with new categories or a separate `EMBEDDED_DISTRO_DATA`.
- Add new facts keys (e.g. `build_system`, `typical_footprint`, `common_targets`).
- Consider a dedicated ASCII style or icon set for embedded systems.
- Update `build_prompt` to produce different emphasis when the flag is present.
- Add to `DistroRenderer` logic.

**Potential version target**: 0.6.0 or 0.7.0 (after the current documentation/examples wave stabilizes).

### `--smallbase` / Minimal / Lightweight Distros
Better support and presentation for very small, resource-friendly distributions.

**Motivation**
- Growing interest in minimal Linux for older hardware, containers, live USBs, privacy, and education.
- These distros have different priorities (boot speed, RAM usage, simplicity) than mainstream ones.

**Examples**
- Puppy Linux (and derivatives)
- Lubuntu / Xubuntu / other lightweight official flavors
- antiX
- MX Linux (light modes)
- Bodhi Linux
- Tiny Core Linux
- Damn Small Linux revivals / modern minimal spins
- Alpine Linux (in minimal configurations)
- Arch Linux + minimal install + lightweight WM

**Possible behaviors**
- `linfo --smallbase` (or `--style smallbase`)
- Emphasize in the fetch view:
  - RAM / storage requirements
  - Default desktop / window manager (or lack thereof)
  - Boot time characteristics
  - Package selection philosophy (minimal base + easy extension)
  - Persistence / frugal install models (especially relevant for Puppy)
- Special sections or facts for "frugal", "live-only", "remastering", etc.

**Rough implementation notes**
- Similar to `--embedded`: new or extended data fields.
- Possibly a different visual treatment in the renderer (smaller/lighter themed panels?).
- LLM prompt tuning to highlight minimalism trade-offs.

**Potential version target**: 0.6.0+

## Backlog / Longer-term or Exploratory Ideas

- Better support for rolling vs point-release characteristics in the output.
- Integration with DistroWatch or other data sources (with proper caching/respect for rate limits).
- `--compare` mode (e.g. `linfo --compare Ubuntu Fedora` or between two architectures of the same distro).
- Machine-readable output (`--json`, `--yaml`) for scripting / embedding in other tools.
- Caching of LLM responses or tool results (with user control and privacy considerations).
- Theming / color scheme options for the Rich output.
- Support for non-x86_64 / non-aarch64 architectures more explicitly in the fastfetch view.
- A TUI mode (using Textual or similar) for interactive exploration.
- First-class support for container / immutable / atomic distros (Fedora Silverblue, NixOS, etc.) with special facts.

## How to Propose or Prioritize Ideas

1. Open a GitHub Discussion or Issue with the `roadmap` or `enhancement` label.
2. Reference this file.
3. When work begins on an item, move the details into the `[Unreleased]` section of `CHANGELOG.md` and create a tracking issue.
4. Follow the guardrails in `.grok/AGENTS.md` when designing the implementation.

## Versioning Note

New capabilities are introduced in **minor** versions (e.g. 0.6.0, 0.7.0) when they are backwards compatible. Significant changes to the output format or CLI contract may warrant a major version bump.

See [CHANGELOG.md](CHANGELOG.md) for the current version and SemVer policy.

---

*This roadmap is aspirational and subject to change based on user feedback, maintainer time, and alignment with the project's design and security guardrails.*