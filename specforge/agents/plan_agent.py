"""Plan Agent sub-agent (ReAct).

Responsibilities:
  * receive complete state from the Supervisor
  * call `check_existing_plan` — reuse an existing plan if present (cost/latency)
  * propose an implementation plan grounded in project context
  * write it via `write_plan_file` to `.claude/plans/<feature-name>.md`
  * update state: plan_path=<path>, status="spec_writing"
"""

from __future__ import annotations

from specforge.state import AgentState


def run_plan_agent(state: AgentState) -> AgentState:
    raise NotImplementedError("run_plan_agent is a scaffold stub — see plans/.")
