"""Runtime settings for SpecForge, loaded from environment / .env."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SPECFORGE_", env_file=".env", extra="ignore")

    # LLM
    model: str = "claude-sonnet-5"
    temperature: float = 0.0
    max_react_iterations: int = 8

    # File I/O scope — the File I/O plugin refuses paths outside these roots.
    plans_dir: Path = Field(default=Path(".claude/plans"))
    spec_dir: Path = Field(default=Path(".claude/spec"))

    # Tracing
    trace_to_stdout: bool = True
    trace_file: Path | None = None

    # Optional FastAPI debug server
    enable_http_dashboard: bool = False
    http_host: str = "127.0.0.1"
    http_port: int = 8765


settings = Settings()
