from __future__ import annotations

import os
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, StrictBool, field_validator

CREATE_TASKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
)
"""


class ErrorResponse(BaseModel):
    error: str


class Task(BaseModel):
    id: int
    title: str
    is_completed: bool
    created_at: str


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


def create_app(database_path: str | None = None) -> FastAPI:
    resolved_database_path = str(database_path or Path(__file__).with_name("tasks.db"))

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        init_db(resolved_database_path)
        yield

    app = FastAPI(
        title="Task Tracker API",
        version="0.1.0",
        description="Tiny FastAPI REST service for tracking tasks.",
        docs_url="/docs",
        openapi_url="/openapi.json",
        redoc_url=None,
        lifespan=lifespan,
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": format_validation_error(exc)},
        )

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    @app.post(
        "/tasks",
        response_model=Task,
        status_code=status.HTTP_201_CREATED,
        responses={400: {"model": ErrorResponse}},
    )
    def create_task(payload: TaskCreate) -> Task:
        created_at = datetime.now(UTC).isoformat(timespec="seconds")

        connection = get_connection(resolved_database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, is_completed, created_at)
                VALUES (?, ?, ?)
                """,
                (payload.title, int(payload.is_completed), created_at),
            )
            connection.commit()
            task = fetch_task_by_id(connection, cursor.lastrowid)
        finally:
            connection.close()

        return Task.model_validate(task)

    @app.get("/tasks", response_model=list[Task])
    def list_tasks() -> list[Task]:
        connection = get_connection(resolved_database_path)
        try:
            rows = connection.execute(
                """
                SELECT id, title, is_completed, created_at
                FROM tasks
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        finally:
            connection.close()

        return [Task.model_validate(row_to_task(row)) for row in rows]

    @app.patch(
        "/tasks/{task_id}",
        response_model=Task,
        responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    )
    def update_task(task_id: int, payload: TaskUpdate) -> Task:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of title or is_completed must be provided.",
            )

        if "is_completed" in updates:
            updates["is_completed"] = int(updates["is_completed"])

        assignments = ", ".join(f"{column} = ?" for column in updates)
        parameters = [*updates.values(), task_id]

        connection = get_connection(resolved_database_path)
        try:
            cursor = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?",
                parameters,
            )
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found.",
                )
            task = fetch_task_by_id(connection, task_id)
        finally:
            connection.close()

        return Task.model_validate(task)

    @app.delete(
        "/tasks/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={404: {"model": ErrorResponse}},
    )
    def delete_task(task_id: int) -> Response:
        connection = get_connection(resolved_database_path)
        try:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            connection.commit()
        finally:
            connection.close()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


def format_validation_error(exc: RequestValidationError) -> str:
    for error in exc.errors():
        field = error["loc"][-1] if error.get("loc") else None
        error_type = error.get("type", "")
        message = error.get("msg", "Request body is invalid.")

        if error_type == "model_attributes_type":
            return "Request body must be a JSON object."
        if field == "title" and error_type == "missing":
            return "title is required and must be a non-empty string."
        if field == "title":
            return message.removeprefix("Value error, ")
        if field == "is_completed":
            return "is_completed must be a boolean when provided."

    return "Request body is invalid."


def init_db(database_path: str) -> None:
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = get_connection(database_path)
    try:
        connection.execute(CREATE_TASKS_TABLE_SQL)
        connection.commit()
    finally:
        connection.close()


def get_connection(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_task_by_id(connection: sqlite3.Connection, task_id: int) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT id, title, is_completed, created_at
        FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"Task {task_id} was not found after persistence.")
    return row_to_task(row)


def row_to_task(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "is_completed": bool(row["is_completed"]),
        "created_at": row["created_at"],
    }


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        reload=os.environ.get("RELOAD", "1") == "1",
    )
