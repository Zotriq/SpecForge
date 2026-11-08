"""FastMCP server exposing SpecForge to Claude Code (stdio transport).

Run with::

    python -m specforge.server
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("specforge")


@mcp.tool()
def forge_spec(request: str) -> dict:
    """Turn a one-line feature request into a spec-driven document.

    Runs the Supervisor -> Plan Agent -> Spec Writer pipeline and returns the
    final state (including ``plan_path`` and ``spec_path``).
    """
    # TODO: call specforge.graph.run(request) and serialise the resulting AgentState.
    raise NotImplementedError("forge_spec is a scaffold stub — see plans/.")


def main() -> None:
    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    main()
