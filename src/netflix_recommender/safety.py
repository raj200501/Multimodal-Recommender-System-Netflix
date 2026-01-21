"""Policy layer to classify and filter recommendations.

This module provides opt-in safety checks for recommendation outputs. Defaults
remain unchanged unless explicitly enabled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import pandas as pd


@dataclass
class SafetyRule:
    name: str
    description: str
    allowed_ratings: Iterable[str]


@dataclass
class SafetyOutcome:
    allowed: bool
    reason: str


@dataclass
class SafetyPolicy:
    """Simple safety policy based on allowlisted ratings."""

    rules: List[SafetyRule] = field(default_factory=list)
    allow_unknown: bool = True

    def evaluate_rating(self, rating: str) -> SafetyOutcome:
        if not self.rules:
            return SafetyOutcome(True, "no-rules")
        for rule in self.rules:
            if rating in rule.allowed_ratings:
                return SafetyOutcome(True, rule.name)
        if self.allow_unknown:
            return SafetyOutcome(True, "unknown-rating-allowed")
        return SafetyOutcome(False, "rating-blocked")

    def apply(
        self, recommendations: pd.DataFrame, rating_column: str = "content_rating"
    ) -> pd.DataFrame:
        output = recommendations.copy()
        if rating_column not in output.columns:
            output["policy_allowed"] = True
            output["policy_reason"] = "no-rating-column"
            return output
        outcomes = output[rating_column].apply(self.evaluate_rating)
        output["policy_allowed"] = outcomes.apply(lambda item: item.allowed)
        output["policy_reason"] = outcomes.apply(lambda item: item.reason)
        return output


def build_default_policy() -> SafetyPolicy:
    return SafetyPolicy(
        rules=[
            SafetyRule(
                name="family_friendly",
                description="Allow family friendly content ratings.",
                allowed_ratings=["G", "PG", "TV-G", "TV-Y"],
            )
        ],
        allow_unknown=True,
    )


def enforce_policy(
    recommendations: pd.DataFrame,
    policy: SafetyPolicy,
    rating_column: str = "content_rating",
    enabled: bool = False,
) -> pd.DataFrame:
    if not enabled:
        return recommendations
    return policy.apply(recommendations, rating_column=rating_column)


def summarize_policy(policy: SafetyPolicy) -> Dict[str, str]:
    return {rule.name: rule.description for rule in policy.rules}
