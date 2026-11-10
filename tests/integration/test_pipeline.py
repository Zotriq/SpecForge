"""Full-pipeline integration tests (LLM calls faked)."""

from __future__ import annotations

from pathlib import Path

import pytest

from specforge.graph import run
from specforge.plugins import file_io


def test_one_line_request_produces_plan_and_spec(fake_llm) -> None:
    llm = fake_llm()
    result = run("I wanna build a wishlist", llm=llm)
    assert result["status"] == "done"
    state = result["state"]
    assert Path(state["plan_path"]).name == "wishlist.md" and Path(state["plan_path"]).parent.name == "plans"
    assert "## Acceptance criteria" in Path(state["spec_path"]).read_text()
    assert len(llm.calls) == 3  # supervisor, plan, spec: no redundant calls
    events = [e["event"] for e in result["trace"]]
    assert events.count("tool_call") == 4  # check_existing_plan, write_plan_file, read_plan_file, write_spec_file
    assert all(e["agent"] for e in result["trace"] if e["event"] == "tool_call")


def test_supervisor_blocks_on_missing_required_field(fake_llm) -> None:
    llm = fake_llm(context={"feature_name": "wishlist", "description": "Save products", "target_layer": None,
                            "data_source": None, "user_facing": True, "tech_stack": "Django + React",
                            "questions": {"target_layer": "Which part of the app is this for?"}})
    result = run("I wanna build a wishlist", llm=llm)
    assert result["status"] == "gathering"
    assert set(result["questions"]) == {"target_layer", "data_source"}
    assert result["questions"]["target_layer"] == "Which part of the app is this for?"
    assert len(llm.calls) == 1  # nothing planned on guessed context


def test_answers_complete_the_context(fake_llm) -> None:
    partial = {"feature_name": "wishlist", "description": "Save products", "target_layer": "storefront",
               "data_source": "postgres.wishlists", "user_facing": True, "tech_stack": "Django + React", "questions": {}}
    result = run("I wanna build a wishlist", answers={"target_layer": "storefront"}, llm=fake_llm(context=partial))
    assert result["status"] == "done"


def test_post_hook_halts_on_bad_agent_output(fake_llm) -> None:
    result = run("I wanna build a wishlist", llm=fake_llm(plan="## Goal\nToo short"))
    assert result["status"] == "error"
    assert "plan_agent output failed validation" in result["error"]
    assert result["state"] is None


def test_existing_plan_is_reused(fake_llm) -> None:
    run("I wanna build a wishlist", llm=fake_llm())
    llm = fake_llm()
    result = run("I wanna build a wishlist", llm=llm)
    assert result["status"] == "done"
    assert not any("Plan Agent" in c for c in llm.calls)  # plan came from disk


def test_file_io_refuses_paths_outside_scope(sandbox) -> None:
    with pytest.raises(file_io.ScopeViolation):
        file_io.write_text(sandbox / "evil.md", "x")
    with pytest.raises(file_io.ScopeViolation):
        file_io.read_text("/etc/passwd")


def test_run_cache_serves_repeat_reads(sandbox) -> None:
    from specforge.config import settings

    cache = file_io.RunCache()
    path = file_io.write_text(settings.plans_dir / "a.md", "hello")
    cache2 = file_io.RunCache()
    assert file_io.read_text(path, cache=cache2) == "hello"
    assert file_io.read_text(path, cache=cache2) == "hello"
    assert cache2.hits == 1 and cache.hits == 0
