"""Data transfer objects for the tasks module.

DTOs sit between storage and API schemas so persistence concerns do not leak
directly into the HTTP layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskDTO:
    id: int
    title: str
    is_completed: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class TaskCreateDTO:
    title: str
    is_completed: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class TaskUpdateDTO:
    title: str | None = None
    is_completed: bool | None = None

    def has_changes(self) -> bool:
        return self.title is not None or self.is_completed is not None
