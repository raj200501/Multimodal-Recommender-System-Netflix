"""Data engineering pipeline for the Netflix demo."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import duckdb
import pandas as pd

from . import analysis_utils, config, database, recommenders

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_data(data_path: Path = config.DATA_PATH) -> pd.DataFrame:
    """Load the synthetic viewing history dataset."""
    logger.info("Extracting synthetic data from %s", data_path)
    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    logger.info("Loaded %d viewing events", len(df))
    return df


def load_raw_data(df: pd.DataFrame, conn: duckdb.DuckDBPyConnection) -> None:
    """Load the raw dataframe into DuckDB as a staging table."""
    logger.info("Loading raw data into staging table raw_views")
    database.write_dataframe(conn, df, "raw_views")


def build_star_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create dimension and fact tables."""
    logger.info("Building dimension and fact tables")
    conn.execute(
        """
        CREATE OR REPLACE TABLE dim_users AS
        SELECT DISTINCT user_id, region, profile
        FROM raw_views;
        """
    )
    conn.execute(
        """
        CREATE OR REPLACE TABLE dim_titles AS
        SELECT DISTINCT show_id AS title_id
        FROM raw_views;
        """
    )
    conn.execute(
        """
        CREATE OR REPLACE TABLE fact_views AS
        SELECT
            user_id,
            show_id AS title_id,
            timestamp,
            device_type,
            watch_time_minutes,
            completion_ratio
        FROM raw_views;
        """
    )
    logger.info("Star schema built: dim_users (%d rows), dim_titles (%d rows), fact_views (%d rows)",
                conn.execute("SELECT COUNT(*) FROM dim_users").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM dim_titles").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM fact_views").fetchone()[0])


def feature_engineering(conn: duckdb.DuckDBPyConnection) -> None:
    """Create feature tables for modeling."""
    logger.info("Generating feature tables")
    conn.execute(
        """
        CREATE OR REPLACE TABLE feat_user_engagement AS
        SELECT user_id, AVG(completion_ratio) AS avg_completion, SUM(watch_time_minutes) AS total_watch_time
        FROM fact_views
        GROUP BY user_id;
        """
    )
    conn.execute(
        """
        CREATE OR REPLACE TABLE feat_title_popularity AS
        SELECT title_id, COUNT(*) AS view_events, AVG(completion_ratio) AS avg_completion
        FROM fact_views
        GROUP BY title_id
        ORDER BY view_events DESC;
        """
    )
    logger.info(
        "Feature tables created (users: %d, titles: %d)",
        conn.execute("SELECT COUNT(*) FROM feat_user_engagement").fetchone()[0],
        conn.execute("SELECT COUNT(*) FROM feat_title_popularity").fetchone()[0],
    )


def train_models(conn: duckdb.DuckDBPyConnection, top_k: int = config.DEFAULT_TOP_K) -> pd.DataFrame:
    """Train baseline recommenders and return combined recommendations."""
    logger.info("Training baseline recommenders with top_k=%d", top_k)
    popularity_recs = recommenders.popularity_recommender(conn, top_k)
    cf_recs = recommenders.user_based_cf(conn, top_k)
    combined = pd.concat([popularity_recs, cf_recs])
    logger.info("Generated %d recommendation rows", len(combined))
    return combined


def evaluate_models(
    df: pd.DataFrame, recommendations: pd.DataFrame, top_k: int = config.DEFAULT_TOP_K
) -> Dict[str, float]:
    """Evaluate recommendations with a simple holdout precision@k."""
    logger.info("Evaluating recommendations with holdout split")
    train_df, test_df = analysis_utils.simple_holdout_split(df)
    truth = analysis_utils.collect_ground_truth(test_df)
    recs_grouped: Dict[str, List[str]] = {}
    for user, group in recommendations.groupby("user_id"):
        recs_grouped[user] = group.sort_values("rank").head(top_k)["title_id"].tolist()
    aligned_truth = {user: truth.get(user, []) for user in recs_grouped.keys()}
    prec = analysis_utils.precision_at_k(recs_grouped, aligned_truth, k=top_k)
    metrics = {"precision_at_k": prec, "test_users": len(aligned_truth)}
    logger.info("Evaluation metrics: %s", metrics)
    return metrics


def run_sql_examples(conn: duckdb.DuckDBPyConnection) -> List:
    """Run example SQL analyses from the sql directory."""
    sql_file = config.SQL_DIR / "engagement_queries.sql"
    if sql_file.exists():
        logger.info("Running sample SQL analyses from %s", sql_file)
        return database.run_query_file(conn, sql_file)
    logger.warning("No SQL file found at %s", sql_file)
    return []


def save_outputs(recommendations: pd.DataFrame, metrics: Dict[str, float]) -> None:
    """Persist outputs to disk."""
    config.ensure_output_dir()
    rec_path = config.OUTPUT_DIR / "recommendations.csv"
    metrics_path = config.OUTPUT_DIR / "metrics.json"
    recommendations.to_csv(rec_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2))
    logger.info("Saved recommendations to %s and metrics to %s", rec_path, metrics_path)


def run_pipeline(data_path: Path = config.DATA_PATH, top_k: int = config.DEFAULT_TOP_K) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Run the full ETL + modeling pipeline."""
    df = extract_data(data_path)
    conn = database.get_connection(config.DB_PATH)
    load_raw_data(df, conn)
    build_star_schema(conn)
    feature_engineering(conn)
    recommendations = train_models(conn, top_k)
    database.write_dataframe(conn, recommendations, "recommendations")
    metrics = evaluate_models(df, recommendations, top_k)
    save_outputs(recommendations, metrics)
    run_sql_examples(conn)
    return recommendations, metrics


if __name__ == "__main__":
    run_pipeline()
