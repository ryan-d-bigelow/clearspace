"""Repository template for a future module.

Replace `Widget` with your domain term and implement the SQLAlchemy methods as
needed. Repositories should return DTOs, not raw ORM models or API schemas.
"""

from __future__ import annotations

from task_tracker.db.sqlite import Database
from task_tracker.modules._template.dtos import WidgetCreateDTO, WidgetDTO, WidgetUpdateDTO


class WidgetRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, payload: WidgetCreateDTO) -> WidgetDTO:
        _ = payload
        raise NotImplementedError("Implement module-specific create persistence here.")

    def list_all(self) -> list[WidgetDTO]:
        raise NotImplementedError("Implement module-specific list persistence here.")

    def get_by_id(self, widget_id: int) -> WidgetDTO | None:
        _ = widget_id
        raise NotImplementedError("Implement module-specific lookup persistence here.")

    def update(self, widget_id: int, changes: WidgetUpdateDTO) -> WidgetDTO | None:
        _ = (widget_id, changes)
        raise NotImplementedError("Implement module-specific update persistence here.")

    def delete(self, widget_id: int) -> bool:
        _ = widget_id
        raise NotImplementedError("Implement module-specific delete persistence here.")
