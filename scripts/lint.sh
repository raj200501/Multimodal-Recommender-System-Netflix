#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if command -v ruff >/dev/null 2>&1; then
  ruff check "$ROOT_DIR/src" "$ROOT_DIR/tests"
elif command -v flake8 >/dev/null 2>&1; then
  flake8 "$ROOT_DIR/src" "$ROOT_DIR/tests"
else
  echo "No linter installed. Install ruff or flake8 to enable lint checks."
fi
