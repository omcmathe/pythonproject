#!/usr/bin/env bash
set -euo pipefail

PYTHON="$(command -v python3 || command -v python)"
if [ -z "$PYTHON" ]; then
    echo "Error: Python is not installed or not in PATH." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    SRCDIR="$SCRIPT_DIR"
else
    REPO="omcmathe/pythonproject"
    BRANCH="${1:-main}"
    TMPDIR="$(mktemp -d)"
    trap 'rm -rf "$TMPDIR"' EXIT

    echo "Downloading $REPO ($BRANCH)..."
    curl -sL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" -o "$TMPDIR/repo.tar.gz"

    echo "Extracting..."
    tar -xzf "$TMPDIR/repo.tar.gz" -C "$TMPDIR"

    SRCDIR="$(find "$TMPDIR" -maxdepth 1 -type d -name "${REPO#*/}-*" | head -n1)"
    if [ -z "$SRCDIR" ]; then
        echo "Error: Could not find extracted source directory." >&2
        exit 1
    fi
fi

echo "Installing with $("$PYTHON" --version)..."
"$PYTHON" -m pip install --quiet "$SRCDIR"

echo "pythonproject installed successfully."
