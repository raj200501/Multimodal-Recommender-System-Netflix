from __future__ import annotations

import pandas as pd

from netflix_recommender.safety import (
    SafetyPolicy,
    SafetyRule,
    build_default_policy,
    enforce_policy,
)


def test_safety_policy_allows_known_rating():
    policy = build_default_policy()
    outcome = policy.evaluate_rating("PG")
    assert outcome.allowed


def test_safety_policy_blocks_when_disabled_unknown():
    policy = SafetyPolicy(
        rules=[SafetyRule(name="kids", description="", allowed_ratings=["G"])],
        allow_unknown=False,
    )
    outcome = policy.evaluate_rating("TV-MA")
    assert not outcome.allowed


def test_enforce_policy_adds_columns():
    policy = build_default_policy()
    recommendations = pd.DataFrame(
        {
            "user_id": ["u1"],
            "title_id": ["s1"],
            "content_rating": ["PG"],
        }
    )
    output = enforce_policy(recommendations, policy, enabled=True)
    assert "policy_allowed" in output.columns
    output["policy_allowed"] = (
        output["policy_allowed"]
        .map(lambda value: True if value else False)
        .astype("object")
    )
    assert output.loc[0, "policy_allowed"] is True


def test_enforce_policy_no_rating_column():
    policy = build_default_policy()
    recommendations = pd.DataFrame({"user_id": ["u1"], "title_id": ["s1"]})
    output = enforce_policy(recommendations, policy, enabled=True)
    assert output.loc[0, "policy_reason"] == "no-rating-column"
