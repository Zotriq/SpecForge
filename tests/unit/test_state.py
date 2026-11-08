"""Unit tests for the shared AgentState model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from specforge.state import AgentState


def test_missing_required_fields_flags_blanks() -> None:
    state = AgentState(
        feature_name="",
        description="   ",
        target_layer="backend",
        data_source="stripe.api",
        user_facing=False,
        tech_stack="FastAPI",
    )
    missing = state.missing_required_fields()
    assert "feature_name" in missing
    assert "description" in missing
    assert "target_layer" not in missing


def test_complete_state_has_no_missing_fields(complete_state: AgentState) -> None:
    assert complete_state.missing_required_fields() == []


def test_target_layer_is_constrained() -> None:
    with pytest.raises(ValidationError):
        AgentState(
            feature_name="x",
            description="x",
            target_layer="mobile",  # not in the allowed literal set
            data_source="x",
            user_facing=True,
            tech_stack="x",
        )


def test_default_status_is_gathering() -> None:
    state = AgentState(
        feature_name="x",
        description="x",
        target_layer="file",
        data_source="x",
        user_facing=False,
        tech_stack="x",
    )
    assert state.status == "gathering"
    assert state.plan_path is None
    assert state.spec_path is None
