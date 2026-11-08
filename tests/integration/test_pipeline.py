"""Full-pipeline integration tests (LLM calls mocked).

These are skipped until the LangGraph graph is implemented — see plans/.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="pipeline not implemented yet — scaffold only")


def test_one_line_request_produces_plan_and_spec() -> None:
    """happy path: 'I wanna build a wishlist' -> plan_path + spec_path set, status='done'."""
    raise NotImplementedError


def test_supervisor_blocks_on_missing_required_field() -> None:
    """Supervisor stays in 'gathering' and asks the user when a field is missing."""
    raise NotImplementedError


def test_post_hook_halts_on_bad_agent_output() -> None:
    """A schema-invalid agent output halts the pipeline with the validation error."""
    raise NotImplementedError
