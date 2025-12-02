"""Analysis and metric utilities for the Netflix recommender demo."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def precision_at_k(recommendations: Dict[str, List[str]], ground_truth: Dict[str, List[str]], k: int) -> float:
    """Compute precision@k across all users."""
    precisions: List[float] = []
    for user_id, recs in recommendations.items():
        truth = set(ground_truth.get(user_id, []))
        if not recs:
            precisions.append(0.0)
            continue
        top_k = set(recs[:k])
        precisions.append(len(top_k & truth) / max(1, min(k, len(top_k))))
    return float(np.mean(precisions)) if precisions else 0.0


def simple_holdout_split(df: pd.DataFrame, cutoff: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a viewing history into train and test sets by timestamp proportion."""
    df_sorted = df.sort_values("timestamp")
    split_idx = int(len(df_sorted) * cutoff)
    return df_sorted.iloc[:split_idx], df_sorted.iloc[split_idx:]


def collect_ground_truth(test_df: pd.DataFrame, min_ratio: float = 0.5) -> Dict[str, List[str]]:
    """Collect ground truth titles with completion above a threshold for each user."""
    truth: Dict[str, List[str]] = {}
    for user, group in test_df.groupby("user_id"):
        truth[user] = group.loc[group["completion_ratio"] >= min_ratio, "show_id"].tolist()
    return truth
