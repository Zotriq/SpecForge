# SpecForge — Implementation Plan (v1)

Status: **DRAFT — awaiting review**
Last updated: 2026-09-10

This plan turns the architecture in [CLAUDE.md](../CLAUDE.md) into an ordered
build. It assumes the scaffold already committed alongside this file (package
skeleton, `pyproject.toml`, stub modules, `test_state.py` passing).

---

## 1. Scope of v1

**In:**

- MCP server (`FastMCP`, stdio) exposing one tool: `forge_spec(request: str)`.
- LangGraph graph running **strictly sequentially**: Supervisor → Plan Agent →
  Spec Writer → END.
- Three ReAct agents (LangChain) sharing one Pydantic `AgentState`.
- Traced tool wrapper; pre-hook (trace) + post-hook (schema validation).
- Scoped File I/O plugin (`.claude/plans/`, `.claude/spec/` only) with a
  per-run read cache.
- Real-time CLI tracing of every tool call and state transition.
- pytest unit + integration suites (LLM mocked).

**Out (deferred):**

- Any parallel / concurrent agent execution.
- FastAPI dashboard beyond a `/health` stub and a read-only trace view.
- Multi-feature batch runs, plan/spec versioning, human-in-the-loop editing UI.
- Persistence beyond flat markdown files + JSONL traces.

---

## 2. Build order (milestones)

Each milestone ends green: `pytest` passes and the relevant slice is
demoable.

### M0 — Scaffold & tooling  *(this commit)*

- [x] Package layout, `pyproject.toml`, `.gitignore`, `README.md`.
- [x] `AgentState` / `PartialContext` models + `test_state.py`.
- [ ] `pip install -e ".[dev]"` verified on a clean venv (Python 3.11+).
- [ ] `ruff` + `mypy --strict` clean on the scaffold.

### M1 — Tracing + hooks foundation

Files: `tracing/logger.py`, `hooks/pre_hook.py`, `hooks/post_hook.py`.

- Rich-backed `emit(event, **fields)` — one styled line per event, never raises;
  optional JSONL mirror to `settings.trace_file`.
- `pre_hook(payload)` — logs agent, tool name, `state_snapshot`, `status_label`,
  and the captured reasoning trace.
- `post_hook.validate_output(agent, raw, schema)` — returns the parsed model or
  raises `PipelineHalt` (wrapping `ValidationError`).
- Tests: `test_tracing.py` (emit shape, no-throw on bad field),
  `test_post_hook.py` (valid parse, halt on invalid).

### M2 — Scoped File I/O plugin

File: `plugins/file_io.py`.

- `_check_scope(path)` — resolve + reject anything outside `plans_dir` /
  `spec_dir`; covers `..` traversal and symlinks.
- `RunCache` — `{abs_path: contents}`, lifetime = one pipeline run.
- `read_text(path, cache=…)` / `write_text(path, contents)` — create parent
  dirs, normalise newlines, populate cache on read/write.
- `CLAUDE.md` read is allowed **read-only** as a special case (project overview)
  — via a separate `read_project_overview()` that caches too.
- Tests: scope allow/deny matrix, traversal attempt, cache hit avoids 2nd read.

### M3 — Traced tool wrapper + tools

Files: `tools/base.py`, `tools/plan_tools.py`, `tools/spec_tools.py`.

- `traced_tool(name, description, input_model, output_model, status_label)` →
  returns a LangChain `StructuredTool` whose `func`:
  1. builds `PreHookPayload` (agent from contextvar, state snapshot) → `pre_hook`
  2. `input_model.model_validate(raw)`
  3. calls the wrapped fn
  4. `output_model.model_validate(result)`
  5. `post_hook` / trace `output`
  6. returns the validated output model
- Agent identity flows via a `contextvars.ContextVar("current_agent")` set by
  each graph node.
- Implement:
  - `check_existing_plan` → `CheckExistingPlanOutput` (uses `RunCache`).
  - `write_plan_file` → writes `.claude/plans/<slug>.md`, returns `plan_path`.
  - `read_plan_file` → cached read.
  - `write_spec_file` → writes `.claude/spec/<slug>.md`, returns `spec_path`.
- `<slug>` = `slugify(feature_name)` (lowercase, `-`, ascii).
- Tests: each tool's happy path + one validation-failure path; assert pre/post
  hooks fired (spy on `emit`).

### M4 — Agents (ReAct)

Files: `agents/supervisor.py`, `agents/plan_agent.py`, `agents/spec_writer.py`,
plus `agents/prompts.py` for prompt templates.

- Shared LLM factory in `config`/`agents/_llm.py` reading `settings.model`,
  `settings.temperature`.
- **Supervisor**:
  - reads project overview once (cached), parses the raw request.
  - fills `PartialContext`; for each field in `missing_required_fields()` emits a
    user-facing question and pauses (LangGraph interrupt or return with
    `status="gathering"` + `questions`).
  - on complete → promote to `AgentState(status="planning")`.
- **Plan Agent**: `check_existing_plan` → reuse or generate → `write_plan_file`
  → `state.plan_path`, `status="spec_writing"`.
- **Spec Writer**: `read_plan_file` → generate 6-section spec doc →
  `write_spec_file` → `state.spec_path`, `status="done"`; return report string.
- Each agent's ReAct loop capped at `settings.max_react_iterations`.
- Tests (mocked LLM via `FakeListChatModel` / responses fixture): each agent
  transitions state correctly and calls only its allowed tools.

### M5 — LangGraph graph

File: `graph.py`.

- `StateGraph(AgentState)` with nodes `supervisor`, `plan_agent`, `spec_writer`.
- Conditional edge from `supervisor`: `"supervisor"` if still gathering, else
  `"plan_agent"`. Linear `plan_agent → spec_writer → END`.
- Node wrappers set the `current_agent` contextvar and run pre/post hooks around
  the agent call.
- `run(raw_request)` builds the graph, invokes with an initial
  `PartialContext(raw_request=…)`, returns final `AgentState`.
- Handle `PipelineHalt` → set `status="error"`, surface message, stop.
- Tests in `tests/integration/test_pipeline.py` (unskip): happy path,
  supervisor-blocks-on-missing-field, post-hook-halt.

### M6 — MCP server wiring

File: `server.py`.

- `forge_spec(request)` → `graph.run(request)` → return
  `state.model_dump()` (plan_path, spec_path, status, + questions if gathering).
- Manual check: register with Claude Code (`claude mcp add`), run end to end.

### M7 — Optional FastAPI debug view

File: `api/app.py`.

- Keep `/health`. Add `/runs` + `/runs/{id}` backed by JSONL trace files.
- Gated by `settings.enable_http_dashboard`; `uvicorn specforge.api.app:app`.

### M8 — Polish

- README quickstart verified, docstrings, `ruff`/`mypy` clean, coverage ≥ 80%
  on `specforge/` minus `api/`.
- Example run committed under `examples/`.

---

## 3. Key design decisions (for review)

| # | Decision | Rationale | Alternative |
|---|----------|-----------|-------------|
| D1 | Supervisor pauses by returning `status="gathering"` + `questions[]` rather than using LangGraph `interrupt()` | Simpler to test; MCP tool call is one-shot, caller re-invokes `forge_spec` with answers | Native `interrupt()` + checkpointer (revisit in v2) |
| D2 | Agent identity via `contextvars` | Keeps `traced_tool` signature clean; works across LangChain callbacks | Pass `agent` explicitly into every tool call |
| D3 | Per-run `RunCache` passed through graph state vs. module singleton | Avoids cross-run leakage in tests / server reuse | Global `lru_cache` (rejected: stale reads) |
| D4 | `CLAUDE.md` readable via a dedicated `read_project_overview()` outside the plans/spec scope | Supervisor needs project context; keeps the general scope rule intact | Widen File I/O scope (rejected: violates plugin contract) |
| D5 | Spec doc = fixed 6 sections (Problem, Requirements, Behaviour, Constraints, Edge Cases, Acceptance Criteria) | Matches the `spec` skill; predictable, gradeable output | Free-form (rejected: hurts accuracy goal) |
| D6 | LLM mocked in all tests via LangChain fake chat models | Deterministic, zero-cost CI | Record/replay cassettes (heavier) |

---

## 4. Risks / open questions

1. **FastMCP + LangGraph event-loop interplay** — FastMCP runs its own asyncio
   loop; `graph.invoke` is sync. Plan: call the sync graph in a thread executor
   from the async tool, or use `graph.ainvoke`. *Confirm during M6.*
2. **Where does the pipeline run relative to the user's project?** `.claude/`
   paths are resolved against CWD. Need to confirm Claude Code launches the MCP
   server with the target project as CWD, else pass a `project_root` arg.
3. **Supervisor re-entry contract** — exact shape of the follow-up call carrying
   user answers. Proposed: `forge_spec(request, answers: dict[str,str] | None)`.
4. **Reasoning trace capture** — LangChain ReAct intermediate steps vs. an
   explicit "think" tool. Leaning on `AgentExecutor`'s
   `return_intermediate_steps=True`.
5. **Model id** — `settings.model` defaults to `claude-sonnet-5`; confirm the
   LangChain provider package to depend on (`langchain-anthropic`).

---

## 5. Definition of done (v1)

- `python -m specforge.server` registers with Claude Code and `forge_spec`
  drives one run start to finish.
- A one-line request produces `.claude/plans/<slug>.md` **and**
  `.claude/spec/<slug>.md`, with `status="done"`.
- Every tool call and state transition is visible in the CLI trace in real time.
- Missing required field ⇒ Supervisor asks, never guesses.
- Bad agent output ⇒ pipeline halts with the Pydantic validation error.
- `pytest` green; `ruff` + `mypy --strict` clean.
