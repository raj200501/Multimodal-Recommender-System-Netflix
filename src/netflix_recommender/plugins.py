"""Plugin architecture for extending the recommendation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Protocol

import pandas as pd


class PipelinePlugin(Protocol):
    """Protocol for pipeline plugins."""

    name: str

    def apply(
        self, recommendations: pd.DataFrame, context: Dict[str, str]
    ) -> pd.DataFrame: ...


@dataclass
class PluginRegistry:
    """In-memory registry for pipeline plugins."""

    plugins: Dict[str, PipelinePlugin] = field(default_factory=dict)

    def register(self, plugin: PipelinePlugin) -> None:
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin {plugin.name} already registered")
        self.plugins[plugin.name] = plugin

    def list_plugins(self) -> List[str]:
        return sorted(self.plugins.keys())

    def apply_all(
        self, recommendations: pd.DataFrame, context: Dict[str, str]
    ) -> pd.DataFrame:
        output = recommendations.copy()
        for plugin in self.plugins.values():
            output = plugin.apply(output, context)
        return output


@dataclass
class PluginContext:
    """Execution context passed to plugins."""

    run_id: str
    stage: str

    def to_dict(self) -> Dict[str, str]:
        return {"run_id": self.run_id, "stage": self.stage}


class EngagementSegmentPlugin:
    """Annotate recommendations with engagement segments."""

    name = "engagement_segment"

    def apply(
        self, recommendations: pd.DataFrame, context: Dict[str, str]
    ) -> pd.DataFrame:
        output = recommendations.copy()
        if "completion_ratio" in output.columns:
            output["engagement_segment"] = pd.cut(
                output["completion_ratio"],
                bins=[0.0, 0.4, 0.7, 1.0],
                labels=["low", "medium", "high"],
                include_lowest=True,
            )
        else:
            output["engagement_segment"] = "unknown"
        output["plugin_context"] = (
            f"{context.get('stage', 'pipeline')}:{context.get('run_id', '')}"
        )
        return output


class ColdStartBoostPlugin:
    """Boost cold-start titles by tagging them for follow-up analysis."""

    name = "cold_start_boost"

    def __init__(self, threshold: int = 2) -> None:
        self.threshold = threshold

    def apply(
        self, recommendations: pd.DataFrame, context: Dict[str, str]
    ) -> pd.DataFrame:
        output = recommendations.copy()
        if "view_events" in output.columns:
            output["cold_start_flag"] = output["view_events"] <= self.threshold
        else:
            output["cold_start_flag"] = False
        return output


def build_default_registry() -> PluginRegistry:
    registry = PluginRegistry()
    registry.register(EngagementSegmentPlugin())
    registry.register(ColdStartBoostPlugin())
    return registry


def apply_plugins(
    recommendations: pd.DataFrame,
    registry: PluginRegistry,
    context: PluginContext,
    enabled: bool = True,
) -> pd.DataFrame:
    if not enabled:
        return recommendations
    return registry.apply_all(recommendations, context.to_dict())


def ensure_required_columns(
    recommendations: pd.DataFrame, columns: Iterable[str]
) -> None:
    missing = [column for column in columns if column not in recommendations.columns]
    if missing:
        raise ValueError(f"Missing required columns for plugins: {', '.join(missing)}")
