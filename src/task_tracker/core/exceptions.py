"""Small domain-level exception types.

Services raise these so business logic stays decoupled from FastAPI.
"""

from __future__ import annotations


class ApplicationError(Exception):
    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BadRequestError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class NotFoundError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)
