"""Supervisor agent (ReAct).

Responsibilities:
  * read the project overview (CLAUDE.md) once, via the cached file reader
  * gather feature context: feature_name, description, target_layer,
    data_source, user_facing, tech_stack
  * ask the user directly for any missing required field — never assume a default
  * once `AgentState.missing_required_fields()` is empty, set status="planning"
    and hand off to the Plan Agent
  * at the end, receive the Spec Writer's report and present the result
"""

from __future__ import annotations

from specforge.state import AgentState, PartialContext


def run_supervisor(state: AgentState | PartialContext) -> AgentState:
    raise NotImplementedError("run_supervisor is a scaffold stub — see plans/.")
