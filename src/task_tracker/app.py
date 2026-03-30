"""Application factory and top-level FastAPI wiring."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from task_tracker import __version__
from task_tracker.api.errors import install_exception_handlers
from task_tracker.api.router import get_api_router
from task_tracker.core.config import Settings, get_settings
from task_tracker.db.bootstrap import initialize_database
from task_tracker.db.sqlite import Database
from task_tracker.modules.tasks.schema import initialize_schema as initialize_tasks_schema

# Register active module schema initializers here.
# Copy `task_tracker.modules._template`, implement the new module, then add its
# schema initializer to this list when you want the module's tables created.
SCHEMA_INITIALIZERS = [initialize_tasks_schema]


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application with all framework-level wiring applied."""

    resolved_settings = settings or get_settings()

    database = Database(resolved_settings.database_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        initialize_database(database, SCHEMA_INITIALIZERS)
        yield

    app = FastAPI(
        title=resolved_settings.app_name,
        version=__version__,
        description=resolved_settings.app_description,
        docs_url=resolved_settings.docs_url,
        openapi_url=resolved_settings.openapi_url,
        redoc_url=resolved_settings.redoc_url,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.database = database

    install_exception_handlers(app)
    app.include_router(get_api_router())

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(
            url=resolved_settings.docs_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    return app


app = create_app()
