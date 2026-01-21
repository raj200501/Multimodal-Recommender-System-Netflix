"""Data engineering pipeline for the Netflix demo."""
from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path
from contextlib import nullcontext
from typing import Dict, List, Tuple

import duckdb
import pandas as pd

from . import analysis_utils, config, database, recommenders
from .observability import MetricRegistry, configure_logging, metric_timer
from .plugins import PluginContext, apply_plugins, build_default_registry
from .quality import DataQualityConfig, run_quality_checks
from .reporting import build_summary, write_markdown_report, write_summary
from .runtime import PipelineRuntimeConfig, runtime_from_env
from .safety import build_default_policy, enforce_policy
from .tracing import TraceRecorder, build_trace_recorder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def resolve_runtime_config(runtime_config: PipelineRuntimeConfig | None) -> PipelineRuntimeConfig:
    """Resolve runtime config from env when none is provided."""
    if runtime_config is not None:
        return runtime_config
    run_id = os.getenv("NETFLIX_REC_RUN_ID", uuid.uuid4().hex)
    return runtime_from_env(run_id)


def ensure_logger(run_id: str, enable_observability: bool) -> logging.Logger:
    if not enable_observability:
        return logger
    structured = configure_logging(service="netflix-recommender", run_id=run_id)
    return structured._logger


def maybe_timer(registry: MetricRegistry | None, name: str) -> nullcontext:
    if registry is None:
        return nullcontext()
    return metric_timer(registry, name)


def maybe_span(recorder: TraceRecorder | None, name: str) -> nullcontext:
    if recorder is None:
        return nullcontext()
    return recorder.span(name)


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


def save_outputs(
    recommendations: pd.DataFrame, metrics: Dict[str, float], output_dir: Path | None = None
) -> None:
    """Persist outputs to disk."""
    resolved_output = output_dir or config.OUTPUT_DIR
    resolved_output.mkdir(parents=True, exist_ok=True)
    rec_path = resolved_output / "recommendations.csv"
    metrics_path = resolved_output / "metrics.json"
    recommendations.to_csv(rec_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2))
    logger.info("Saved recommendations to %s and metrics to %s", rec_path, metrics_path)


def run_pipeline(
    data_path: Path = config.DATA_PATH,
    top_k: int = config.DEFAULT_TOP_K,
    runtime_config: PipelineRuntimeConfig | None = None,
    metrics_registry: MetricRegistry | None = None,
    trace_recorder: TraceRecorder | None = None,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Run the full ETL + modeling pipeline."""

    runtime_config = resolve_runtime_config(runtime_config)
    structured_logger = (
        configure_logging("netflix-recommender", runtime_config.run_id)
        if runtime_config.enable_observability
        else None
    )
    trace_recorder = trace_recorder or (
        build_trace_recorder(runtime_config.trace_path, run_id=runtime_config.run_id, enabled=runtime_config.enable_tracing)
        if runtime_config.trace_path is not None
        else None
    )
    if metrics_registry is None and runtime_config.enable_metrics:
        metrics_registry = MetricRegistry()

    with maybe_span(trace_recorder, "extract"):
        with maybe_timer(metrics_registry, "extract_data"):
            df = extract_data(data_path)

    if runtime_config.enable_quality_checks:
        quality_config = DataQualityConfig(
            min_rows=1,
            required_columns=["user_id", "show_id", "timestamp", "completion_ratio"],
            numeric_ranges={"completion_ratio": (0.0, 1.0)},
        )
        raw_report = run_quality_checks(df, quality_config, dataset="raw_views")
        quality_path = runtime_config.quality_report_path or (runtime_config.output_dir / "quality_report.json")
        quality_path.parent.mkdir(parents=True, exist_ok=True)
        quality_path.write_text(json.dumps(raw_report.to_dict(), indent=2))
        if structured_logger:
            structured_logger.info("Quality checks completed", passed=raw_report.passed(), path=str(quality_path))

    with maybe_span(trace_recorder, "connect"):
        with maybe_timer(metrics_registry, "connect_db"):
            conn = database.get_connection(runtime_config.db_path)

    with maybe_span(trace_recorder, "load_raw"):
        with maybe_timer(metrics_registry, "load_raw"):
            load_raw_data(df, conn)

    with maybe_span(trace_recorder, "star_schema"):
        with maybe_timer(metrics_registry, "build_star_schema"):
            build_star_schema(conn)

    with maybe_span(trace_recorder, "feature_engineering"):
        with maybe_timer(metrics_registry, "feature_engineering"):
            feature_engineering(conn)

    with maybe_span(trace_recorder, "train_models"):
        with maybe_timer(metrics_registry, "train_models"):
            recommendations = train_models(conn, top_k)

    database.write_dataframe(conn, recommendations, "recommendations")

    if runtime_config.enable_plugins:
        registry = build_default_registry()
        plugin_context = PluginContext(run_id=runtime_config.run_id, stage="post_recommendation")
        recommendations = apply_plugins(recommendations, registry, plugin_context, enabled=True)
        if structured_logger:
            structured_logger.info("Applied plugins", plugins=registry.list_plugins())

    if runtime_config.enable_policy:
        policy = build_default_policy()
        recommendations = enforce_policy(recommendations, policy, enabled=True)
        if structured_logger:
            structured_logger.info("Applied safety policy", rules=[rule.name for rule in policy.rules])

    with maybe_span(trace_recorder, "evaluate"):
        with maybe_timer(metrics_registry, "evaluate"):
            metrics = evaluate_models(df, recommendations, top_k)

    save_outputs(recommendations, metrics, output_dir=runtime_config.output_dir)
    summary = build_summary(recommendations)
    write_summary(summary, runtime_config.output_dir / "summary.json")
    write_markdown_report(summary, metrics, runtime_config.output_dir / "pipeline_report.md")
    run_sql_examples(conn)

    if structured_logger:
        structured_logger.info("Pipeline complete", metrics=metrics)
    return recommendations, metrics


if __name__ == "__main__":
    run_pipeline()
