"""Trace recording utilities for pipeline runs.

Traces are stored as JSONL for easy inspection and converted to Markdown for
recruiter-friendly demos. Tracing is opt-in and disabled by default.
"""

from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional


@dataclass
class TraceEvent:
    event: str
    timestamp: float
    run_id: str
    span_id: Optional[str] = None
    parent_id: Optional[str] = None
    payload: Dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "event": self.event,
                "timestamp": self.timestamp,
                "run_id": self.run_id,
                "span_id": self.span_id,
                "parent_id": self.parent_id,
                "payload": self.payload,
            },
            sort_keys=True,
        )


@dataclass
class TraceSpan:
    recorder: "TraceRecorder"
    name: str
    span_id: str
    parent_id: Optional[str]
    start_time: float

    def end(self, **payload: str) -> None:
        self.recorder.record_event(
            "span.end",
            span_id=self.span_id,
            parent_id=self.parent_id,
            payload={"name": self.name, **payload},
        )


@dataclass
class TraceRecorder:
    path: Path
    run_id: str
    enabled: bool = True

    def record_event(
        self,
        event: str,
        span_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        payload: Optional[Dict[str, str]] = None,
    ) -> None:
        if not self.enabled:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        trace_event = TraceEvent(
            event=event,
            timestamp=time.time(),
            run_id=self.run_id,
            span_id=span_id,
            parent_id=parent_id,
            payload=payload or {},
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(trace_event.to_json())
            handle.write("\n")

    @contextmanager
    def span(
        self, name: str, parent_id: Optional[str] = None, **payload: str
    ) -> Iterator[TraceSpan]:
        if not self.enabled:
            yield TraceSpan(
                self,
                name=name,
                span_id="disabled",
                parent_id=parent_id,
                start_time=time.time(),
            )
            return
        span_id = uuid.uuid4().hex
        self.record_event(
            "span.start",
            span_id=span_id,
            parent_id=parent_id,
            payload={"name": name, **payload},
        )
        span = TraceSpan(
            self,
            name=name,
            span_id=span_id,
            parent_id=parent_id,
            start_time=time.time(),
        )
        try:
            yield span
        finally:
            duration_ms = int((time.time() - span.start_time) * 1000)
            span.end(duration_ms=str(duration_ms))

    def export_markdown(self, markdown_path: Path) -> None:
        events = self.read_events()
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Trace Report", "", f"Run ID: `{self.run_id}`", ""]
        for event in events:
            payload = ", ".join(
                f"{key}={value}" for key, value in event.payload.items()
            )
            lines.append(
                f"- **{event.event}** @ {event.timestamp:.3f}s span={event.span_id or '-'} parent={event.parent_id or '-'} {payload}"
            )
        markdown_path.write_text("\n".join(lines), encoding="utf-8")

    def read_events(self) -> List[TraceEvent]:
        if not self.path.exists():
            return []
        events: List[TraceEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            events.append(
                TraceEvent(
                    event=payload["event"],
                    timestamp=payload["timestamp"],
                    run_id=payload["run_id"],
                    span_id=payload.get("span_id"),
                    parent_id=payload.get("parent_id"),
                    payload=payload.get("payload", {}),
                )
            )
        return events


def build_trace_recorder(
    trace_path: Path, run_id: Optional[str] = None, enabled: bool = True
) -> TraceRecorder:
    return TraceRecorder(
        path=trace_path, run_id=run_id or uuid.uuid4().hex, enabled=enabled
    )
