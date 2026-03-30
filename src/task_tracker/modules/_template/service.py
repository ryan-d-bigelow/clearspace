"""Service template for a future module.

Keep business rules here. Route handlers should stay thin and repositories
should stay focused on storage concerns. Services should translate API schemas
to DTOs before calling repositories.
"""

from __future__ import annotations

from task_tracker.modules._template.repository import WidgetRepository
from task_tracker.modules._template.schemas import Widget, WidgetCreate, WidgetUpdate


class WidgetService:
    def __init__(self, repository: WidgetRepository) -> None:
        self.repository = repository

    def create_widget(self, payload: WidgetCreate) -> Widget:
        _ = payload.to_dto(created_at="replace-me")
        raise NotImplementedError("Implement module-specific create logic here.")

    def list_widgets(self) -> list[Widget]:
        raise NotImplementedError("Implement module-specific list logic here.")

    def update_widget(self, widget_id: int, payload: WidgetUpdate) -> Widget:
        _ = (widget_id, payload.to_dto())
        raise NotImplementedError("Implement module-specific update logic here.")

    def delete_widget(self, widget_id: int) -> None:
        _ = widget_id
        raise NotImplementedError("Implement module-specific delete logic here.")
