"""Observability utilities for the recommender pipeline.

This module provides structured logging and a lightweight metrics registry that
can be enabled via environment flags. Default behavior remains unchanged unless
explicitly enabled.
"""

from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional


@dataclass
class LogContext:
    """Structured logging context appended to each log line."""

    service: str
    environment: str
    run_id: str
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "service": self.service,
            "environment": self.environment,
            "run_id": self.run_id,
        }
        payload.update(self.extra)
        return payload


class StructuredLogger:
    """Structured logger that emits JSON or plain text entries."""

    def __init__(
        self, logger: logging.Logger, context: LogContext, json_output: bool = True
    ) -> None:
        self._logger = logger
        self._context = context
        self._json_output = json_output

    def _emit(self, level: int, message: str, **fields: Any) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "level": logging.getLevelName(level),
            "context": self._context.to_dict(),
            "fields": fields,
        }
        if self._json_output:
            self._logger.log(level, json.dumps(record, sort_keys=True))
        else:
            merged = " ".join(f"{key}={value}" for key, value in fields.items())
            self._logger.log(level, f"{message} {merged}".strip())

    def info(self, message: str, **fields: Any) -> None:
        self._emit(logging.INFO, message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._emit(logging.WARNING, message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit(logging.ERROR, message, **fields)


@dataclass
class MetricSample:
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: float


@dataclass
class MetricRegistry:
    """In-process metrics registry for counters, gauges, and timers."""

    counters: Dict[str, float] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)
    histograms: Dict[str, List[MetricSample]] = field(default_factory=dict)

    def increment(
        self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None
    ) -> None:
        self.counters[name] = self.counters.get(name, 0.0) + value
        self._record(name, value, tags or {})

    def set_gauge(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        self.gauges[name] = value
        self._record(name, value, tags or {})

    def observe(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        self._record(name, value, tags or {})

    def _record(self, name: str, value: float, tags: Dict[str, str]) -> None:
        bucket = self.histograms.setdefault(name, [])
        bucket.append(
            MetricSample(name=name, value=value, tags=tags, timestamp=time.time())
        )

    @contextmanager
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.observe(name, elapsed, tags or {})

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                key: [sample.__dict__ for sample in samples]
                for key, samples in self.histograms.items()
            },
        }


@contextmanager
def metric_timer(
    registry: MetricRegistry, name: str, tags: Optional[Dict[str, str]] = None
) -> Iterator[None]:
    with registry.timer(name, tags=tags):
        yield


def configure_logging(
    service: str,
    run_id: str,
    environment: Optional[str] = None,
    json_output: Optional[bool] = None,
    level: int = logging.INFO,
) -> StructuredLogger:
    """Configure structured logging and return a structured logger instance."""
    logger = logging.getLogger(service)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)

    env = environment or os.getenv("NETFLIX_REC_ENV", "local")
    json_enabled = (
        json_output
        if json_output is not None
        else os.getenv("STRUCTURED_LOG_JSON", "1") == "1"
    )
    context = LogContext(service=service, environment=env, run_id=run_id)
    return StructuredLogger(logger, context, json_output=json_enabled)


def maybe_setup_otel(service_name: str) -> bool:
    """Optional OpenTelemetry scaffolding; returns True if configured."""
    enabled = os.getenv("ENABLE_OTEL", "0") == "1"
    if not enabled:
        return False
    import importlib.util

    if importlib.util.find_spec("opentelemetry") is None:
        return False
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    return True


def build_metric_tags(**kwargs: str) -> Dict[str, str]:
    return {key: value for key, value in kwargs.items() if value is not None}


def normalize_fields(
    fields: Dict[str, Any], include_keys: Iterable[str]
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key in include_keys:
        if key in fields:
            result[key] = fields[key]
    return result
