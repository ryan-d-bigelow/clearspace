"""HTTP routes for the tasks module."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from task_tracker.api.dependencies import get_database
from task_tracker.api.errors import ErrorResponse
from task_tracker.db.sqlite import Database
from task_tracker.modules.tasks.repository import TaskRepository
from task_tracker.modules.tasks.schemas import Task, TaskCreate, TaskUpdate
from task_tracker.modules.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(database: Annotated[Database, Depends(get_database)]) -> TaskService:
    """Compose the task service for each request.

    If the module later needs more collaborators, wire them here.
    """

    return TaskService(TaskRepository(database))


@router.post(
    "",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_task(
    payload: TaskCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    return service.create_task(payload)


@router.get("", response_model=list[Task])
def list_tasks(service: Annotated[TaskService, Depends(get_task_service)]) -> list[Task]:
    return service.list_tasks()


@router.patch(
    "/{task_id}",
    response_model=Task,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    return service.update_task(task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
