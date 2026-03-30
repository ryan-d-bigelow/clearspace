"""Business logic for tasks.

Keep this layer free of FastAPI imports so it stays easy to test and reuse.
"""

from __future__ import annotations

from datetime import UTC, datetime

from task_tracker.core.exceptions import BadRequestError, NotFoundError
from task_tracker.modules.tasks.repository import TaskRepository
from task_tracker.modules.tasks.schemas import Task, TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(self, payload: TaskCreate) -> Task:
        task = self.repository.create(payload.to_dto(created_at=self._timestamp()))
        return Task.from_dto(task)

    def list_tasks(self) -> list[Task]:
        return [Task.from_dto(task) for task in self.repository.list_all()]

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        updates = payload.to_dto()
        if not updates.has_changes():
            raise BadRequestError("At least one of title or is_completed must be provided.")

        task = self.repository.update(task_id, updates)
        if task is None:
            raise NotFoundError("Task not found.")
        return Task.from_dto(task)

    def delete_task(self, task_id: int) -> None:
        deleted = self.repository.delete(task_id)
        if not deleted:
            raise NotFoundError("Task not found.")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
