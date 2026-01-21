#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

WORK_DIR=$(mktemp -d)
export WORK_DIR
cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

python - <<'PY'
import os
from pathlib import Path
from netflix_recommender.demo import run_demo_in_dir

tmp_dir = Path(os.environ["WORK_DIR"])
result, summary = run_demo_in_dir(tmp_dir)
print(summary)

assert (result.output_dir / "recommendations.csv").exists(), "missing recommendations.csv"
assert (result.output_dir / "metrics.json").exists(), "missing metrics.json"
assert result.trace_path.exists(), "missing trace file"
assert result.trace_markdown_path.exists(), "missing trace markdown"
assert result.quality_report_path.exists(), "missing quality report"
assert result.summary_path.exists(), "missing summary json"
assert (result.output_dir / "pipeline_report.md").exists(), "missing pipeline report"
print("DEMO PASS")
PY
