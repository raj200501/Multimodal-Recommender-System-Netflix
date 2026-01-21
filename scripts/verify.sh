#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

python -m pip install -r "$ROOT_DIR/requirements.txt" >/dev/null
PIP_NO_BUILD_ISOLATION=1 python -m pip install -e "$ROOT_DIR" --no-build-isolation >/dev/null

if command -v black >/dev/null 2>&1; then
  black --check \
    "$ROOT_DIR/src/netflix_recommender/observability.py" \
    "$ROOT_DIR/src/netflix_recommender/tracing.py" \
    "$ROOT_DIR/src/netflix_recommender/plugins.py" \
    "$ROOT_DIR/src/netflix_recommender/safety.py" \
    "$ROOT_DIR/src/netflix_recommender/runtime.py" \
    "$ROOT_DIR/src/netflix_recommender/demo.py" \
    "$ROOT_DIR/src/netflix_recommender/quality.py" \
    "$ROOT_DIR/src/netflix_recommender/reporting.py" \
    "$ROOT_DIR/tests/test_observability.py" \
    "$ROOT_DIR/tests/test_tracing.py" \
    "$ROOT_DIR/tests/test_plugins.py" \
    "$ROOT_DIR/tests/test_safety.py" \
    "$ROOT_DIR/tests/test_runtime.py" \
    "$ROOT_DIR/tests/test_demo.py" \
    "$ROOT_DIR/tests/test_pipeline_extensions.py" \
    "$ROOT_DIR/tests/test_quality.py" \
    "$ROOT_DIR/tests/test_reporting.py"
else
  echo "black not installed; skipping format check"
fi

if command -v ruff >/dev/null 2>&1; then
  ruff check "$ROOT_DIR/src" "$ROOT_DIR/tests"
elif command -v flake8 >/dev/null 2>&1; then
  flake8 "$ROOT_DIR/src" "$ROOT_DIR/tests"
else
  echo "ruff/flake8 not installed; skipping lint"
fi

if command -v mypy >/dev/null 2>&1; then
  mypy "$ROOT_DIR/src/netflix_recommender"
else
  echo "mypy not installed; skipping type check"
fi

pytest -q

bash "$ROOT_DIR/scripts/demo.sh"
