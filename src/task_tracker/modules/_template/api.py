"""HTTP route template for a future module.

This package is intentionally not registered in ``task_tracker.api.router``.
Copy it, rename symbols, implement the service methods, then wire it in.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from task_tracker.api.dependencies import get_database
from task_tracker.api.errors import ErrorResponse
from task_tracker.db.sqlite import Database
from task_tracker.modules._template.repository import WidgetRepository
from task_tracker.modules._template.schemas import Widget, WidgetCreate, WidgetUpdate
from task_tracker.modules._template.service import WidgetService

router = APIRouter(prefix="/widgets", tags=["widgets"])


def get_widget_service(database: Annotated[Database, Depends(get_database)]) -> WidgetService:
    """Compose the module's service from shared dependencies."""

    return WidgetService(WidgetRepository(database))


@router.post(
    "",
    response_model=Widget,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_widget(
    payload: WidgetCreate,
    service: Annotated[WidgetService, Depends(get_widget_service)],
) -> Widget:
    return service.create_widget(payload)


@router.get("", response_model=list[Widget])
def list_widgets(service: Annotated[WidgetService, Depends(get_widget_service)]) -> list[Widget]:
    return service.list_widgets()


@router.patch(
    "/{widget_id}",
    response_model=Widget,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_widget(
    widget_id: int,
    payload: WidgetUpdate,
    service: Annotated[WidgetService, Depends(get_widget_service)],
) -> Widget:
    return service.update_widget(widget_id, payload)


@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_widget(
    widget_id: int,
    service: Annotated[WidgetService, Depends(get_widget_service)],
) -> Response:
    service.delete_widget(widget_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
