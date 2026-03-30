"""Database bootstrap orchestration."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from task_tracker.db.sqlite import Database

SchemaInitializer = Callable[[Database], None]


def initialize_database(database: Database, initializers: Sequence[SchemaInitializer]) -> None:
    """Run all module schema initializers.

    Add new module initializers in ``task_tracker.app.SCHEMA_INITIALIZERS``.
    """

    for initializer in initializers:
        initializer(database)
