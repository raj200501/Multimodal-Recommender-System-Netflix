from __future__ import annotations

from pathlib import Path

from netflix_recommender import config
from netflix_recommender.data_pipeline import run_pipeline
from netflix_recommender.runtime import build_runtime_config


def test_run_pipeline_with_runtime_config(tmp_path: Path):
    output_dir = tmp_path / "outputs"
    runtime_config = build_runtime_config(
        run_id="run-1",
        output_dir=output_dir,
        db_path=tmp_path / "pipeline.db",
        trace_path=output_dir / "trace.jsonl",
        enable_observability=False,
        enable_tracing=False,
        enable_plugins=True,
        enable_policy=True,
        enable_metrics=False,
        enable_quality_checks=True,
        quality_report_path=output_dir / "quality_report.json",
    )

    recommendations, metrics = run_pipeline(
        data_path=config.DATA_PATH, runtime_config=runtime_config
    )
    assert not recommendations.empty
    assert "precision_at_k" in metrics
    assert (output_dir / "recommendations.csv").exists()
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "pipeline_report.md").exists()
    assert (output_dir / "quality_report.json").exists()
