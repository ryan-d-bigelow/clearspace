"""Schema initializer template for a future module.

Register ORM models for the module and then create them from here when the
module becomes active.
"""

from __future__ import annotations

from task_tracker.db.base import Base
from task_tracker.db.sqlite import Database
from task_tracker.modules._template.models import WidgetRecord


def initialize_schema(database: Database) -> None:
    """Create any tables needed by the module."""

    _ = WidgetRecord
    Base.metadata.create_all(bind=database.engine)
