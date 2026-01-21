from __future__ import annotations

from pathlib import Path

from netflix_recommender import config
from netflix_recommender.runtime import build_runtime_config


def test_build_runtime_config_defaults(tmp_path: Path):
    runtime_config = build_runtime_config(run_id="run-1")
    assert runtime_config.output_dir == config.OUTPUT_DIR
    assert runtime_config.db_path == config.DB_PATH


def test_build_runtime_config_overrides(tmp_path: Path):
    output_dir = tmp_path / "outputs"
    db_path = tmp_path / "demo.db"
    runtime_config = build_runtime_config(
        run_id="run-2", output_dir=output_dir, db_path=db_path
    )
    assert runtime_config.output_dir == output_dir
    assert runtime_config.db_path == db_path
