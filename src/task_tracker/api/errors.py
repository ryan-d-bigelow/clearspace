"""Shared API error handling.

Keep transport-specific error shaping here so services and repositories stay
framework-agnostic.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from task_tracker.core.exceptions import ApplicationError


class ErrorResponse(BaseModel):
    error: str


def install_exception_handlers(app: FastAPI) -> None:
    """Install app-wide exception handlers in one place."""

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        _: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(status_code=exc.status_code, content={"error": detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": format_validation_error(exc)},
        )


def format_validation_error(exc: RequestValidationError) -> str:
    """Translate Pydantic/FastAPI validation output into interview-friendly errors."""

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
