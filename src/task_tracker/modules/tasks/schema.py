"""Schema initialization for the tasks module.

When you add a new module with its own tables, create its schema initializer in
that module and register it from ``task_tracker.app.SCHEMA_INITIALIZERS``.
"""

from __future__ import annotations

from task_tracker.db.base import Base
from task_tracker.db.sqlite import Database
from task_tracker.modules.tasks.models import TaskRecord


def initialize_schema(database: Database) -> None:
    """Create the tables owned by the tasks module."""

    _ = TaskRecord
    Base.metadata.create_all(bind=database.engine)
