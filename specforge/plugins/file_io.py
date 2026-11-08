"""Scoped File I/O plugin.

Read/write access is restricted to ``.claude/plans/`` and ``.claude/spec/``.
Any path that resolves outside those roots raises :class:`ScopeViolation`.

Also provides a per-run read cache so the same resource (e.g. ``CLAUDE.md``,
an existing plan file) is never fetched twice within a single pipeline run.
"""

from __future__ import annotations

from pathlib import Path

from specforge.config import settings


class ScopeViolation(PermissionError):
    """Raised when a path escapes the allowed plans/spec roots."""


def _allowed_roots() -> tuple[Path, ...]:
    return (settings.plans_dir.resolve(), settings.spec_dir.resolve())


def _check_scope(path: Path) -> Path:
    resolved = path.resolve()
    if not any(resolved == root or root in resolved.parents for root in _allowed_roots()):
        raise ScopeViolation(f"{resolved} is outside the allowed plans/spec roots")
    return resolved


class RunCache:
    """Content cache keyed by absolute path, lifetime == one pipeline run."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, path: str) -> str | None:
        return self._store.get(path)

    def put(self, path: str, contents: str) -> None:
        self._store[path] = contents


def read_text(path: str | Path, *, cache: RunCache | None = None) -> str:
    raise NotImplementedError("read_text is a scaffold stub — see plans/.")


def write_text(path: str | Path, contents: str) -> str:
    raise NotImplementedError("write_text is a scaffold stub — see plans/.")
