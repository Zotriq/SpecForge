"""Spec Writer tools: read_plan_file (shared), write_spec_file.

All file access goes through the scoped File I/O plugin
(``specforge.plugins.file_io``) — restricted to ``.claude/spec/`` for writes
and ``.claude/plans/`` for the plan read.
"""

from __future__ import annotations

from pydantic import BaseModel


class WriteSpecFileInput(BaseModel):
    feature_name: str
    markdown: str


class WriteSpecFileOutput(BaseModel):
    spec_path: str


# TODO: implement write_spec_file as a `@traced_tool(...)`-decorated function.
# read_plan_file is re-exported from specforge.tools.plan_tools.
