from __future__ import annotations

import json
import logging
from netflix_recommender.observability import (
    MetricRegistry,
    build_metric_tags,
    configure_logging,
    normalize_fields,
)


def test_configure_logging_emits_json(caplog):
    caplog.set_level(logging.INFO)
    logger = configure_logging(service="test-service", run_id="run-1", json_output=True)
    logger.info("hello", key="value")

    assert caplog.records
    payload = json.loads(caplog.records[-1].message)
    assert payload["message"] == "hello"
    assert payload["context"]["service"] == "test-service"
    assert payload["fields"]["key"] == "value"


def test_metric_registry_records_samples():
    registry = MetricRegistry()
    registry.increment("requests", value=2)
    registry.set_gauge("load", value=0.5)
    registry.observe("latency", value=0.12)

    snapshot = registry.snapshot()
    assert snapshot["counters"]["requests"] == 2
    assert snapshot["gauges"]["load"] == 0.5
    assert snapshot["histograms"]["latency"]


def test_metric_registry_timer_records_latency():
    registry = MetricRegistry()
    with registry.timer("timed_op"):
        pass
    assert registry.histograms["timed_op"], "timer should emit a sample"


def test_build_metric_tags_filters_none():
    tags = build_metric_tags(region="na", stage=None)
    assert tags == {"region": "na"}


def test_normalize_fields_extracts_keys():
    fields = {"a": 1, "b": 2, "c": 3}
    assert normalize_fields(fields, ["a", "c"]) == {"a": 1, "c": 3}
