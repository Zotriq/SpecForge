# SpecForge

Sequential multi-agent CLI tool that turns a one-line feature request
("I wanna build X") into a structured, spec-driven document.

SpecForge runs as an MCP server connected to Claude Code and orchestrates
three agents that hand off a single shared state object in sequence, with
every tool call traced:

1. **Supervisor** — gathers feature context, asks the user for anything missing.
2. **Plan Agent** — proposes an implementation plan, writes `.claude/plans/<feature>.md`.
3. **Spec Writer** — turns the plan into a spec-driven doc, writes `.claude/spec/<feature>.md`.

## Goals (priority order)

1. High accuracy — specs grounded in real project context, never guessed.
2. Full traceability — every tool call and state transition logged to the CLI in real time.
3. Minimum cost & latency — no redundant LLM calls or repeated file reads.
4. Strict sequential workflow — one agent at a time, fixed order, no concurrency in v1.

## Tech stack

| Concern | Library |
| --- | --- |
| Orchestration graph & state | LangGraph |
| Agent construction (ReAct), tool binding, prompts | LangChain |
| MCP server (stdio transport) | FastMCP |
| Optional tracing dashboard / debug HTTP endpoints | FastAPI |
| Schemas & output validation | Pydantic |
| Tests | pytest |

## Getting started

```bash
py -m venv .venv
.venv\Scripts\activate           # Windows
pip install -e ".[dev]"
```

## Commands

- `pytest` — run all unit and integration tests
- `pytest tests/unit` — agent/tool-level tests only
- `pytest tests/integration` — full pipeline runs (mocked LLM calls)
- `python -m specforge.server` — start the MCP server (stdio transport)

## Layout

```
specforge/
  server.py       FastMCP server entrypoint (stdio)
  state.py        AgentState Pydantic model
  graph.py        LangGraph graph: Supervisor -> Plan Agent -> Spec Writer
  config.py       Runtime settings
  agents/         ReAct agents: supervisor, plan_agent, spec_writer
  tools/          Traced tool wrapper + plan/spec file tools
  hooks/          Pre-hook (trace) and post-hook (schema validation)
  plugins/        Scoped file I/O (.claude/plans/, .claude/spec/ only)
  tracing/        Real-time CLI trace logger
  api/            Optional FastAPI debug/dashboard app
tests/
  unit/           Per agent/tool tests
  integration/    Full pipeline runs with mocked LLMs
plans/            Implementation planning docs (reviewed before build)
```

See [CLAUDE.md](CLAUDE.md) for the full architecture spec.
