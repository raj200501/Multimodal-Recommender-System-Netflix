"""Runtime configuration for pipeline execution."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import config


@dataclass
class PipelineRuntimeConfig:
    run_id: str
    output_dir: Path
    db_path: Path
    trace_path: Optional[Path]
    enable_observability: bool = False
    enable_tracing: bool = False
    enable_plugins: bool = False
    enable_policy: bool = False
    enable_metrics: bool = False
    enable_quality_checks: bool = False
    quality_report_path: Optional[Path] = None


def build_runtime_config(
    run_id: str,
    output_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    trace_path: Optional[Path] = None,
    enable_observability: bool = False,
    enable_tracing: bool = False,
    enable_plugins: bool = False,
    enable_policy: bool = False,
    enable_metrics: bool = False,
    enable_quality_checks: bool = False,
    quality_report_path: Optional[Path] = None,
) -> PipelineRuntimeConfig:
    resolved_output_dir = output_dir or config.OUTPUT_DIR
    resolved_db_path = db_path or config.DB_PATH
    return PipelineRuntimeConfig(
        run_id=run_id,
        output_dir=resolved_output_dir,
        db_path=resolved_db_path,
        trace_path=trace_path,
        enable_observability=enable_observability,
        enable_tracing=enable_tracing,
        enable_plugins=enable_plugins,
        enable_policy=enable_policy,
        enable_metrics=enable_metrics,
        enable_quality_checks=enable_quality_checks,
        quality_report_path=quality_report_path,
    )


def runtime_from_env(run_id: str) -> PipelineRuntimeConfig:
    output_override = os.getenv("NETFLIX_REC_OUTPUT_DIR")
    db_override = os.getenv("NETFLIX_REC_DB_PATH")
    trace_override = os.getenv("NETFLIX_REC_TRACE_PATH")
    quality_report_override = os.getenv("NETFLIX_REC_QUALITY_REPORT")
    return build_runtime_config(
        run_id=run_id,
        output_dir=Path(output_override) if output_override else None,
        db_path=Path(db_override) if db_override else None,
        trace_path=Path(trace_override) if trace_override else None,
        enable_observability=os.getenv("ENABLE_OBSERVABILITY", "0") == "1",
        enable_tracing=os.getenv("ENABLE_TRACING", "0") == "1",
        enable_plugins=os.getenv("ENABLE_PLUGINS", "0") == "1",
        enable_policy=os.getenv("ENABLE_POLICY", "0") == "1",
        enable_metrics=os.getenv("ENABLE_METRICS", "0") == "1",
        enable_quality_checks=os.getenv("ENABLE_QUALITY_CHECKS", "0") == "1",
        quality_report_path=(
            Path(quality_report_override) if quality_report_override else None
        ),
    )
