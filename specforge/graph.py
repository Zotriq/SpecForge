"""LangGraph orchestration graph.

Fixed sequential order (v1, no concurrency):

    supervisor -> plan_agent -> spec_writer -> END

Each node receives and returns :class:`specforge.state.AgentState`. The
Supervisor may loop back on itself while it is still gathering required
context from the user.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from specforge.state import AgentState

if TYPE_CHECKING:  # pragma: no cover
    from langgraph.graph import StateGraph


def build_graph() -> "StateGraph":
    """Construct and compile the SpecForge LangGraph graph.

    TODO:
      * add nodes: supervisor, plan_agent, spec_writer
      * conditional edge out of supervisor: stay while `missing_required_fields()`
        is non-empty, else advance to plan_agent
      * linear edges plan_agent -> spec_writer -> END
      * attach pre-hook (trace) and post-hook (schema validation) around nodes
    """
    raise NotImplementedError("build_graph() is a scaffold stub — see plans/.")


def run(raw_request: str) -> AgentState:
    """Entry used by the MCP tool / CLI: run the full pipeline for one request."""
    raise NotImplementedError("run() is a scaffold stub — see plans/.")
