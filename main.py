#!/usr/bin/env python3
"""Compatibility shim — the real CLI lives in the `linfo` package.

Prefer one of:
  uv run linfo --help
  uv tool install . && linfo --help
  python -m linfo --help
"""

from linfo.main import main

if __name__ == "__main__":
    main()
