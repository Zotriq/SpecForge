"""Shared pytest fixtures."""

from __future__ import annotations

import json

import pytest

from specforge.config import settings
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


@pytest.fixture(autouse=True)
def sandbox(tmp_path, monkeypatch):
    """Point the plans/spec roots and project overview at a temp folder."""
    monkeypatch.setattr(settings, "plans_dir", tmp_path / ".claude" / "plans")
    monkeypatch.setattr(settings, "spec_dir", tmp_path / ".claude" / "spec")
    monkeypatch.setattr(settings, "project_overview", tmp_path / "CLAUDE.md")
    monkeypatch.setattr(settings, "trace_to_stdout", False)
    (tmp_path / "CLAUDE.md").write_text("Shop app: Django REST backend, React storefront, PostgreSQL.")
    return tmp_path


PLAN = """# Wishlist plan
## Goal
Let signed-in shoppers save products and see them later.
## Approach
Add a Wishlist model in Django with a REST endpoint and a React heart button on product cards.
## Steps
1. Add `Wishlist` and `WishlistItem` models plus a migration in `shop/models.py`.
2. Add `GET/POST/DELETE /api/wishlist/` views and serializers.
3. Add a heart toggle to `ProductCard.tsx` and a `/wishlist` page.
## Risks
Anonymous users have no account; keep the button hidden for them.
"""

SPEC = """# Wishlist spec
## Overview
Shoppers can save products to a personal wishlist from any product card.
## Requirements
1. Signed-in shoppers can add and remove products.
2. The wishlist page lists saved products newest first.
## Data model
WishlistItem(user_id, product_id, created_at), unique on (user_id, product_id).
## Interfaces
GET/POST/DELETE /api/wishlist/ ; React `useWishlist()` hook.
## Acceptance criteria
1. Given a signed-in shopper, when they tap the heart, then the product appears on /wishlist.
## Out of scope
Sharing wishlists; price-drop alerts.
"""


class FakeLLM:
    """Answers each agent by looking at its system prompt; records calls."""

    def __init__(self, context: dict | None = None, plan: str = PLAN, spec: str = SPEC):
        self.context = context if context is not None else {
            "feature_name": "wishlist", "description": "Let shoppers save products to a wishlist.",
            "target_layer": "storefront", "data_source": "postgres.wishlists", "user_facing": True,
            "tech_stack": "Django + React", "questions": {}}
        self.plan, self.spec, self.calls = plan, spec, []

    def __call__(self, system: str, user: str) -> str:
        self.calls.append(system.split(".")[0])
        if "Supervisor" in system:
            return json.dumps(self.context)
        if "Plan Agent" in system:
            return self.plan
        return self.spec


@pytest.fixture
def fake_llm():
    return FakeLLM
