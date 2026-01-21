#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

python - <<'PY'
import importlib.util
import platform
import sys

print("Python:", sys.version)
print("Platform:", platform.platform())

required = ["numpy", "pandas", "duckdb", "sklearn", "pytest", "matplotlib"]
missing = []
for package in required:
    if importlib.util.find_spec(package) is None:
        missing.append(package)

if missing:
    print("Missing packages:", ", ".join(missing))
    print("Install with: pip install -r requirements.txt")
    raise SystemExit(1)

print("All required packages detected.")
PY

if [[ -d "$ROOT_DIR/frontend" ]]; then
  if command -v node >/dev/null 2>&1; then
    echo "Node: $(node --version)"
  else
    echo "Node not found; frontend demo requires Node.js"
  fi
fi
