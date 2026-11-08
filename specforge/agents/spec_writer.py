"""Spec Writer sub-agent (ReAct).

Responsibilities:
  * receive state + plan from the Plan Agent
  * read the plan via `read_plan_file` (served from the run cache when possible)
  * write a spec-driven doc via `write_spec_file` to `.claude/spec/<feature-name>.md`
  * update state: spec_path=<path>, status="done"
  * report the result back to the Supervisor
"""

from __future__ import annotations

from specforge.state import AgentState


def run_spec_writer(state: AgentState) -> AgentState:
    raise NotImplementedError("run_spec_writer is a scaffold stub — see plans/.")
