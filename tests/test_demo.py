from __future__ import annotations

from pathlib import Path

from netflix_recommender.demo import run_demo_in_dir


def test_run_demo_creates_outputs(tmp_path: Path):
    result, summary = run_demo_in_dir(tmp_path)

    assert "Demo Summary" in summary
    assert (result.output_dir / "recommendations.csv").exists()
    assert (result.output_dir / "metrics.json").exists()
    assert result.trace_path.exists()
    assert result.trace_markdown_path.exists()
