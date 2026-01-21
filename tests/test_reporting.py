from __future__ import annotations

from pathlib import Path

import pandas as pd

from netflix_recommender.reporting import (
    build_summary,
    list_output_files,
    write_markdown_report,
    write_summary,
)


def sample_recommendations() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2"],
            "title_id": ["s1", "s2", "s3"],
            "model": ["popularity", "cf", "cf"],
        }
    )


def test_build_summary_counts():
    summary = build_summary(sample_recommendations())
    assert summary.total_rows == 3
    assert summary.unique_users == 2
    assert summary.unique_titles == 3
    assert summary.top_models["cf"] == 2


def test_write_summary_and_markdown(tmp_path: Path):
    summary = build_summary(sample_recommendations())
    summary_path = tmp_path / "summary.json"
    write_summary(summary, summary_path)
    assert summary_path.exists()

    report_path = tmp_path / "report.md"
    write_markdown_report(summary, {"precision_at_k": 0.5}, report_path)
    assert report_path.exists()


def test_list_output_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    files = list_output_files(tmp_path)
    assert len(files) == 2
