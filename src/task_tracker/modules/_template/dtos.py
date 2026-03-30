"""DTO template for a future module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WidgetDTO:
    id: int
    name: str
    created_at: str


@dataclass(frozen=True, slots=True)
class WidgetCreateDTO:
    name: str
    created_at: str


@dataclass(frozen=True, slots=True)
class WidgetUpdateDTO:
    name: str | None = None

    def has_changes(self) -> bool:
        return self.name is not None
