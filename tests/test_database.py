from netflix_recommender import config, data_pipeline, database


def test_star_schema_created(tmp_path, monkeypatch):
    temp_db = tmp_path / "warehouse.db"
    monkeypatch.setattr(config, "DB_PATH", temp_db)
    df = data_pipeline.extract_data(config.DATA_PATH)
    conn = database.get_connection(temp_db)
    data_pipeline.load_raw_data(df, conn)
    data_pipeline.build_star_schema(conn)

    assert conn.execute("SELECT COUNT(*) FROM dim_users").fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM dim_titles").fetchone()[0] > 0
    assert conn.execute("PRAGMA table_info('fact_views')").fetchall()
