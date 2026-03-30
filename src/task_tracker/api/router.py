"""Aggregate application router.

When you add a new feature module:
1. Copy `task_tracker.modules._template` to a new module package.
2. Implement the module.
3. Import its router here and include it below.
"""

from fastapi import APIRouter

from task_tracker.modules.tasks.api import router as tasks_router


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(tasks_router)
    return router
