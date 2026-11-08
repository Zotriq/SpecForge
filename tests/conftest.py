"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from specforge.state import AgentState


@pytest.fixture
def complete_state() -> AgentState:
    """A fully-populated AgentState for tests that need a valid handoff object."""
    return AgentState(
        feature_name="wishlist",
        description="Let shoppers save products to a wishlist.",
        target_layer="storefront",
        data_source="postgres.wishlists",
        user_facing=True,
        tech_stack="Django + React",
        status="planning",
    )
