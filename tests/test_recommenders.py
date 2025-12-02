from netflix_recommender import config, data_pipeline, database, recommenders


def test_recommenders_produce_results(tmp_path, monkeypatch):
    temp_db = tmp_path / "rec.db"
    monkeypatch.setattr(config, "DB_PATH", temp_db)
    df = data_pipeline.extract_data(config.DATA_PATH)
    conn = database.get_connection(temp_db)
    data_pipeline.load_raw_data(df, conn)
    data_pipeline.build_star_schema(conn)

    pop = recommenders.popularity_recommender(conn, top_k=2)
    cf = recommenders.user_based_cf(conn, top_k=2)

    assert not pop.empty
    assert not cf.empty
    assert set(pop.columns) == {"user_id", "title_id", "rank", "model"}
    assert set(cf.columns) == {"user_id", "title_id", "rank", "model"}
