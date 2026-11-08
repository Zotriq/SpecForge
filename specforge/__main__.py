"""CLI entrypoint for SpecForge.

For v1 the primary interface is the MCP server (``python -m specforge.server``).
This module exists so ``specforge`` is runnable as a console script and can grow
a Typer/argparse CLI later (e.g. ``specforge run "I wanna build X"``).
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # TODO: wire up argument parsing and dispatch to the LangGraph pipeline.
    print("SpecForge v0.1.0 — run `python -m specforge.server` to start the MCP server.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
