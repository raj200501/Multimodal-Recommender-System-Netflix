from __future__ import annotations

from pathlib import Path

from netflix_recommender.tracing import build_trace_recorder


def test_trace_recorder_writes_events(tmp_path: Path):
    trace_path = tmp_path / "trace.jsonl"
    recorder = build_trace_recorder(trace_path, run_id="run-1", enabled=True)

    recorder.record_event("pipeline.start", payload={"stage": "extract"})
    with recorder.span("extract"):
        pass

    events = recorder.read_events()
    assert events
    assert events[0].event == "pipeline.start"


def test_trace_recorder_exports_markdown(tmp_path: Path):
    trace_path = tmp_path / "trace.jsonl"
    recorder = build_trace_recorder(trace_path, run_id="run-2", enabled=True)

    recorder.record_event("pipeline.start")
    with recorder.span("train"):
        pass

    markdown_path = tmp_path / "trace.md"
    recorder.export_markdown(markdown_path)
    content = markdown_path.read_text(encoding="utf-8")
    assert "Trace Report" in content
    assert "pipeline.start" in content
