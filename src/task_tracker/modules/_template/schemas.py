"""Pydantic model template for a future module."""

from __future__ import annotations

from dataclasses import asdict

from pydantic import BaseModel, ConfigDict

from task_tracker.modules._template.dtos import WidgetCreateDTO, WidgetDTO, WidgetUpdateDTO


class Widget(BaseModel):
    id: int
    name: str
    created_at: str

    @classmethod
    def from_dto(cls, dto: WidgetDTO) -> Widget:
        return cls.model_validate(asdict(dto))


class WidgetCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str

    def to_dto(self, *, created_at: str) -> WidgetCreateDTO:
        return WidgetCreateDTO(name=self.name, created_at=created_at)


class WidgetUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None

    def to_dto(self) -> WidgetUpdateDTO:
        values = self.model_dump(exclude_unset=True)
        return WidgetUpdateDTO(name=values.get("name"))
