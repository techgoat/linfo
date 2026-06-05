#!/usr/bin/env bash
# linfo CLI Usage Examples
# Make executable: chmod +x examples/cli-examples.sh
# Run individual lines or the whole script (it will prompt for API key if not set).

set -e

echo "=== Random distro (defaults to fastfetch-style + in-depth) ==="
uv run linfo

echo ""
echo "=== Brief mode for a known distro (compact, no long panel) ==="
uv run linfo --distro Ubuntu --brief

echo ""
echo "=== Brief for an arbitrary/less-common distro (graceful fallback to compact summary) ==="
uv run linfo --distro "Parrot Security" --brief

echo ""
echo "=== Force markdown style with specific level and topics ==="
uv run linfo --distro Fedora --style markdown --level intermediate --topics "package management,security"

echo ""
echo "=== Verbose (internal logs on console + always to logs/transaction_log.txt) ==="
uv run linfo --distro Arch -v --brief

echo ""
echo "=== Architecture-specific ==="
uv run linfo --distro "Debian" --arch aarch64 --brief

echo ""
echo "Done. See docs/ and README.md for more."
