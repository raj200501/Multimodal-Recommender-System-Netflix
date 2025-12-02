"""Baseline recommender implementations."""
from __future__ import annotations

import logging
from typing import List

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def popularity_recommender(conn: duckdb.DuckDBPyConnection, top_k: int) -> pd.DataFrame:
    """Recommend the most popular titles overall."""
    logger.info("Computing popularity-based recommendations")
    popularity = conn.execute(
        """
        SELECT title_id, COUNT(*) AS views, AVG(completion_ratio) AS avg_completion
        FROM fact_views
        GROUP BY title_id
        ORDER BY views DESC, avg_completion DESC;
        """
    ).df()
    users = conn.execute("SELECT DISTINCT user_id FROM fact_views").df()["user_id"].tolist()
    rows = []
    for user in users:
        for rank, (_, row) in enumerate(popularity.iterrows(), start=1):
            if rank > top_k:
                break
            rows.append({"user_id": user, "title_id": row["title_id"], "rank": rank, "model": "popularity"})
    return pd.DataFrame(rows)


def user_based_cf(conn: duckdb.DuckDBPyConnection, top_k: int) -> pd.DataFrame:
    """Simple user-based collaborative filtering using cosine similarity."""
    logger.info("Computing user-based collaborative filtering recommendations")
    interactions = conn.execute(
        """
        SELECT user_id, title_id, completion_ratio
        FROM fact_views
        """
    ).df()
    pivot = interactions.pivot_table(index="user_id", columns="title_id", values="completion_ratio", fill_value=0)
    similarity = cosine_similarity(pivot)
    sim_df = pd.DataFrame(similarity, index=pivot.index, columns=pivot.index)

    recommendations: List[dict] = []
    for user_id in pivot.index:
        # compute weighted scores
        user_sim = sim_df.loc[user_id]
        for title in pivot.columns:
            if pivot.loc[user_id, title] > 0:
                continue
            scores = []
            for other_user in pivot.index:
                if other_user == user_id:
                    continue
                score = user_sim[other_user]
                scores.append(score * pivot.loc[other_user, title])
            mean_score = float(np.mean(scores)) if scores else 0.0
            recommendations.append({"user_id": user_id, "title_id": title, "score": mean_score})

    rec_df = pd.DataFrame(recommendations)
    if rec_df.empty:
        logger.warning("No CF recommendations generated")
        return pd.DataFrame(columns=["user_id", "title_id", "rank", "model"])
    rec_df["rank"] = rec_df.groupby("user_id")["score"].rank("dense", ascending=False)
    filtered = rec_df.sort_values(["user_id", "rank"]).groupby("user_id").head(top_k)
    filtered["model"] = "user_cf"
    return filtered[["user_id", "title_id", "rank", "model"]]
