"""Traced tool wrapper.

Every SpecForge tool is defined with Pydantic input/output models and wrapped
by :func:`traced_tool`, which:

  * fires the pre-hook (log calling agent, tool name, state snapshot, status label)
  * validates the raw input against the tool's input model
  * invokes the underlying callable
  * validates the return value against the tool's output model
  * fires the post-hook
  * returns a LangChain-compatible ``StructuredTool``

There is intentionally no path to call a tool without this wrapper.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from langchain_core.tools import StructuredTool

TIn = TypeVar("TIn", bound=BaseModel)
TOut = TypeVar("TOut", bound=BaseModel)


def traced_tool(
    *,
    name: str,
    description: str,
    input_model: type[TIn],
    output_model: type[TOut],
    status_label: str,
) -> Callable[[Callable[[TIn], TOut]], "StructuredTool"]:
    """Decorator that turns a typed function into a traced ``StructuredTool``."""

    def decorator(fn: Callable[[TIn], TOut]) -> "StructuredTool":
        raise NotImplementedError("traced_tool is a scaffold stub — see plans/.")

    return decorator
