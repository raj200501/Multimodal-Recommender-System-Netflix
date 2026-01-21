"""Demo utilities for recruiter-friendly walkthroughs."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from . import config, data_pipeline, runtime
from .observability import MetricRegistry, configure_logging
from .tracing import build_trace_recorder


@dataclass
class DemoResult:
    run_id: str
    output_dir: Path
    recommendations: pd.DataFrame
    metrics: Dict[str, float]
    trace_path: Path
    trace_markdown_path: Path
    quality_report_path: Path
    summary_path: Path


def run_demo(output_dir: Path) -> DemoResult:
    """Run the pipeline with tracing and observability enabled in a temp directory."""
    run_id = uuid.uuid4().hex
    trace_path = output_dir / "traces" / f"trace_{run_id}.jsonl"
    trace_markdown_path = output_dir / "traces" / f"trace_{run_id}.md"
    logger = configure_logging(service="netflix-demo", run_id=run_id)
    metrics_registry = MetricRegistry()
    trace_recorder = build_trace_recorder(
        trace_path=trace_path, run_id=run_id, enabled=True
    )

    runtime_config = runtime.build_runtime_config(
        run_id=run_id,
        output_dir=output_dir,
        db_path=output_dir / "demo.db",
        trace_path=trace_path,
        enable_observability=True,
        enable_tracing=True,
        enable_plugins=True,
        enable_policy=True,
        enable_metrics=True,
        enable_quality_checks=True,
        quality_report_path=output_dir / "quality_report.json",
    )

    logger.info("Starting demo run", output_dir=str(output_dir))
    recommendations, metrics = data_pipeline.run_pipeline(
        data_path=config.DATA_PATH,
        top_k=config.DEFAULT_TOP_K,
        runtime_config=runtime_config,
        metrics_registry=metrics_registry,
        trace_recorder=trace_recorder,
    )
    trace_recorder.export_markdown(trace_markdown_path)
    metrics_path = output_dir / "metrics_snapshot.json"
    metrics_path.write_text(json.dumps(metrics_registry.snapshot(), indent=2))
    logger.info("Demo run complete", metrics_path=str(metrics_path))

    return DemoResult(
        run_id=run_id,
        output_dir=output_dir,
        recommendations=recommendations,
        metrics=metrics,
        trace_path=trace_path,
        trace_markdown_path=trace_markdown_path,
        quality_report_path=output_dir / "quality_report.json",
        summary_path=output_dir / "summary.json",
    )


def format_demo_summary(result: DemoResult) -> str:
    summary = [
        "Demo Summary:",
        f"- Run ID: {result.run_id}",
        f"- Output Dir: {result.output_dir}",
        f"- Recommendations: {len(result.recommendations)} rows",
        f"- Metrics: {result.metrics}",
        f"- Trace JSONL: {result.trace_path}",
        f"- Trace Markdown: {result.trace_markdown_path}",
        f"- Quality Report: {result.quality_report_path}",
        f"- Summary JSON: {result.summary_path}",
    ]
    return "\n".join(summary)


def run_demo_in_dir(output_dir: Path) -> Tuple[DemoResult, str]:
    result = run_demo(output_dir)
    summary = format_demo_summary(result)
    return result, summary
