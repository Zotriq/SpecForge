"""Pre-hook — runs before every tool call.

Logs, via the real-time CLI tracer:
  * calling agent
  * tool name
  * a snapshot of current AgentState
  * a status label: reading_file | understanding | generating_plan | writing_spec | output

Also captures the agent's chain-of-thought reasoning trace for the step
(never discarded).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

StatusLabel = Literal[
    "reading_file", "understanding", "generating_plan", "writing_spec", "output"
]


class PreHookPayload(BaseModel):
    agent: str
    tool_name: str
    status_label: StatusLabel
    state_snapshot: dict
    reasoning: str | None = None


def pre_hook(payload: PreHookPayload) -> None:
    raise NotImplementedError("pre_hook is a scaffold stub — see plans/.")
