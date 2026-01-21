from __future__ import annotations

import pandas as pd

from netflix_recommender.plugins import (
    ColdStartBoostPlugin,
    EngagementSegmentPlugin,
    PluginContext,
    PluginRegistry,
    apply_plugins,
    build_default_registry,
    ensure_required_columns,
)


def sample_recommendations() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2"],
            "title_id": ["s1", "s2", "s3"],
            "rank": [1, 2, 1],
            "completion_ratio": [0.2, 0.8, 0.6],
            "view_events": [1, 3, 2],
        }
    )


def test_registry_registers_plugins():
    registry = PluginRegistry()
    registry.register(EngagementSegmentPlugin())
    registry.register(ColdStartBoostPlugin())
    assert registry.list_plugins() == ["cold_start_boost", "engagement_segment"]


def test_plugins_apply_to_dataframe():
    registry = build_default_registry()
    context = PluginContext(run_id="run-1", stage="test")
    output = apply_plugins(sample_recommendations(), registry, context, enabled=True)
    assert "engagement_segment" in output.columns
    assert "cold_start_flag" in output.columns


def test_plugins_disabled_returns_input():
    registry = build_default_registry()
    context = PluginContext(run_id="run-1", stage="test")
    input_df = sample_recommendations()
    output = apply_plugins(input_df, registry, context, enabled=False)
    assert output.equals(input_df)


def test_ensure_required_columns_raises():
    df = pd.DataFrame({"user_id": ["u1"]})
    try:
        ensure_required_columns(df, ["title_id"])
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
