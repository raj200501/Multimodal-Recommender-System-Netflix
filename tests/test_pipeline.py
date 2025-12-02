import pandas as pd

from netflix_recommender import config, data_pipeline


def test_run_pipeline(tmp_path, monkeypatch):
    temp_db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", temp_db)
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    config.ensure_output_dir()

    recommendations, metrics = data_pipeline.run_pipeline(config.DATA_PATH, top_k=3)

    assert not recommendations.empty
    assert "precision_at_k" in metrics
    assert (tmp_path / "recommendations.csv").exists()
    assert (tmp_path / "metrics.json").exists()

    # verify recommendations persisted to DuckDB
    conn = data_pipeline.database.get_connection(temp_db)
    count = conn.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
    assert count == len(recommendations)
