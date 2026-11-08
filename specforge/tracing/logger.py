"""Structured, real-time trace logger (Rich-backed).

Emits one line per event to the CLI as it happens — tool calls, state
transitions, agent handoffs, reasoning traces — so a run is fully auditable
while it executes. Optionally mirrors events to ``settings.trace_file``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from specforge.config import settings


def emit(event: str, **fields: Any) -> None:
    """Emit a single trace event. Never raises — tracing must not break a run."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    if settings.trace_to_stdout:
        # TODO: swap for a Rich console with per-event styling.
        print(record)
    # TODO: append `record` as JSONL to settings.trace_file when set.
