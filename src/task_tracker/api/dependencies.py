"""Shared FastAPI dependencies.

This is the right place for app-wide dependency providers such as:
- settings
- database clients
- authentication context
- shared request metadata
"""

from __future__ import annotations

from typing import cast

from fastapi import Request

from task_tracker.core.config import Settings
from task_tracker.db.sqlite import Database


def get_settings(request: Request) -> Settings:
    """Return the application settings stored during app creation."""

    return cast(Settings, request.app.state.settings)


def get_database(request: Request) -> Database:
    """Create the shared database abstraction for a request."""

    return cast(Database, request.app.state.database)
