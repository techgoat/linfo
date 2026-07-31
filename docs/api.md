# API Reference

This page is auto-generated from the source using [mkdocstrings](https://mkdocstrings.github.io/).

## Package

::: linfo
    options:
      show_root_heading: true
      show_source: false
      docstring_style: google

## CLI orchestration

::: linfo.main
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

## Data & models

::: linfo.data
    options:
      show_root_heading: true
      show_source: false
      docstring_style: google

::: linfo.models
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

## Rendering & output

::: linfo.renderer
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

::: linfo.output
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

## Agent & secrets

::: linfo.agent
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

::: linfo.secrets
    options:
      show_root_heading: true
      show_source: true
      docstring_style: google

The main public surface consists of:

- `Distro` dataclass
- `DistroRenderer` dataclass (the core of `--style`, `--brief`, and `--embedded` presentation)
- Helpers: `get_distro_data`, `normalize_distro_name`, `build_prompt`, `build_result_payload`
- `main()` (the CLI entrypoint)

For usage examples, see the [Usage](usage.md) page and the `examples/` directory.
