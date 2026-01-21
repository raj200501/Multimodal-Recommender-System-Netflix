"""Reporting helpers for pipeline outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd


@dataclass
class RecommendationSummary:
    total_rows: int
    unique_users: int
    unique_titles: int
    top_models: Dict[str, int]

    def to_dict(self) -> Dict[str, object]:
        return {
            "total_rows": self.total_rows,
            "unique_users": self.unique_users,
            "unique_titles": self.unique_titles,
            "top_models": self.top_models,
        }


def build_summary(recommendations: pd.DataFrame) -> RecommendationSummary:
    total_rows = len(recommendations)
    unique_users = (
        recommendations["user_id"].nunique()
        if "user_id" in recommendations.columns
        else 0
    )
    unique_titles = (
        recommendations["title_id"].nunique()
        if "title_id" in recommendations.columns
        else 0
    )
    top_models = (
        recommendations["model"].value_counts().head(5).to_dict()
        if "model" in recommendations.columns
        else {}
    )
    return RecommendationSummary(
        total_rows=total_rows,
        unique_users=unique_users,
        unique_titles=unique_titles,
        top_models=top_models,
    )


def write_summary(summary: RecommendationSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")


def write_markdown_report(
    summary: RecommendationSummary, metrics: Dict[str, float], path: Path
) -> None:
    lines = [
        "# Pipeline Report",
        "",
        "## Recommendation Summary",
        f"- Total rows: {summary.total_rows}",
        f"- Unique users: {summary.unique_users}",
        f"- Unique titles: {summary.unique_titles}",
    ]
    if summary.top_models:
        lines.append("- Top models:")
        for model, count in summary.top_models.items():
            lines.append(f"  - {model}: {count}")
    lines.extend(["", "## Metrics"])
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def read_recommendations(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def list_output_files(output_dir: Path) -> List[Path]:
    if not output_dir.exists():
        return []
    return sorted([path for path in output_dir.iterdir() if path.is_file()])
