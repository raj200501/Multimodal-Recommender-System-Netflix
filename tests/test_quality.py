from __future__ import annotations

import pandas as pd

from netflix_recommender.quality import DataQualityConfig, run_quality_checks


def test_quality_checks_pass():
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u2"],
            "show_id": ["s1", "s2"],
            "timestamp": ["2024-01-01", "2024-01-02"],
            "completion_ratio": [0.5, 0.9],
        }
    )
    config = DataQualityConfig(
        min_rows=1,
        required_columns=["user_id", "show_id"],
        numeric_ranges={"completion_ratio": (0.0, 1.0)},
    )
    report = run_quality_checks(df, config, dataset="raw")
    assert report.passed()


def test_quality_checks_fail_for_missing_columns():
    df = pd.DataFrame({"user_id": ["u1"]})
    config = DataQualityConfig(min_rows=1, required_columns=["user_id", "show_id"])
    report = run_quality_checks(df, config, dataset="raw")
    assert not report.passed()
    assert any(check.name == "required_columns" for check in report.checks)
