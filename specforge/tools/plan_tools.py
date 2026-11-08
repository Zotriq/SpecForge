"""Plan Agent tools: check_existing_plan, write_plan_file, read_plan_file.

All file access goes through the scoped File I/O plugin
(``specforge.plugins.file_io``) — restricted to ``.claude/plans/``.
"""

from __future__ import annotations

from pydantic import BaseModel


class CheckExistingPlanInput(BaseModel):
    feature_name: str


class CheckExistingPlanOutput(BaseModel):
    exists: bool
    plan_path: str | None = None
    contents: str | None = None


class WritePlanFileInput(BaseModel):
    feature_name: str
    markdown: str


class WritePlanFileOutput(BaseModel):
    plan_path: str


class ReadPlanFileInput(BaseModel):
    plan_path: str


class ReadPlanFileOutput(BaseModel):
    contents: str


# TODO: implement each as a `@traced_tool(...)`-decorated function.
