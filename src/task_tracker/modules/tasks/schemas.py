"""Pydantic request/response models for tasks."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pydantic import BaseModel, ConfigDict, StrictBool, field_validator

from task_tracker.modules.tasks.dtos import TaskCreateDTO, TaskDTO, TaskUpdateDTO


class Task(BaseModel):
    id: int
    title: str
    is_completed: bool
    created_at: str

    @classmethod
    def from_dto(cls, dto: TaskDTO) -> Task:
        return cls.model_validate(asdict(dto))


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    is_completed: StrictBool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title is required and must be a non-empty string.")
        return stripped

    def to_dto(self, *, created_at: str) -> TaskCreateDTO:
        return TaskCreateDTO(
            title=self.title,
            is_completed=self.is_completed,
            created_at=created_at,
        )


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str | None = None
    is_completed: StrictBool | None = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: Any) -> str:
        if value is None:
            raise ValueError("title must be a non-empty string when provided.")
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must be a non-empty string when provided.")
        return stripped

    def to_dto(self) -> TaskUpdateDTO:
        values = self.model_dump(exclude_unset=True)
        return TaskUpdateDTO(
            title=values.get("title"),
            is_completed=values.get("is_completed"),
        )
