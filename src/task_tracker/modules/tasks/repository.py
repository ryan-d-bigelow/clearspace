"""SQLAlchemy-backed data access for tasks."""

from __future__ import annotations

from sqlalchemy import select

from task_tracker.db.sqlite import Database
from task_tracker.modules.tasks.dtos import TaskCreateDTO, TaskDTO, TaskUpdateDTO
from task_tracker.modules.tasks.models import TaskRecord


class TaskRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, dto: TaskCreateDTO) -> TaskDTO:
        with self.database.session() as session:
            record = TaskRecord(
                title=dto.title,
                is_completed=dto.is_completed,
                created_at=dto.created_at,
            )
            session.add(record)
            session.flush()
            session.refresh(record)

        return to_dto(record)

    def list_all(self) -> list[TaskDTO]:
        statement = select(TaskRecord).order_by(TaskRecord.created_at.desc(), TaskRecord.id.desc())
        with self.database.session() as session:
            records = session.scalars(statement).all()
        return [to_dto(record) for record in records]

    def update(self, task_id: int, dto: TaskUpdateDTO) -> TaskDTO | None:
        if not dto.has_changes():
            return self.get_by_id(task_id)

        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                return None
            if dto.title is not None:
                record.title = dto.title
            if dto.is_completed is not None:
                record.is_completed = dto.is_completed
            session.flush()
            session.refresh(record)
            return to_dto(record)

    def delete(self, task_id: int) -> bool:
        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
            if record is None:
                return False
            session.delete(record)
            return True

    def get_by_id(self, task_id: int) -> TaskDTO | None:
        with self.database.session() as session:
            record = session.get(TaskRecord, task_id)
        return to_dto(record) if record is not None else None


def to_dto(record: TaskRecord) -> TaskDTO:
    return TaskDTO(
        id=record.id,
        title=record.title,
        is_completed=record.is_completed,
        created_at=record.created_at,
    )
