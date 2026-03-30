"""Framework-agnostic configuration objects."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the application."""

    app_name: str = "Task Tracker API"
    app_description: str = "Tiny FastAPI REST service for tracking tasks."
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str | None = None
    database_path: str = str(Path(__file__).resolve().parents[3] / "tasks.db")


@lru_cache
def get_settings() -> Settings:
    """Build settings once per process from environment defaults."""

    return Settings(
        app_name=os.environ.get("APP_NAME", "Task Tracker API"),
        app_description=os.environ.get(
            "APP_DESCRIPTION",
            "Tiny FastAPI REST service for tracking tasks.",
        ),
        docs_url=os.environ.get("DOCS_URL", "/docs"),
        openapi_url=os.environ.get("OPENAPI_URL", "/openapi.json"),
        redoc_url=os.environ.get("REDOC_URL") or None,
        database_path=os.environ.get(
            "DATABASE_PATH",
            str(Path(__file__).resolve().parents[3] / "tasks.db"),
        ),
    )
