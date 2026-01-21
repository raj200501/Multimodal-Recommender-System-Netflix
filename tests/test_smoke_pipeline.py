from __future__ import annotations

from netflix_recommender import config, data_pipeline


def test_extract_data_smoke():
    df = data_pipeline.extract_data(config.DATA_PATH)
    assert not df.empty
    assert {"user_id", "show_id"}.issubset(df.columns)
