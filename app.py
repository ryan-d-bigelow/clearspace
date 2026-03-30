"""Thin compatibility entrypoint for local runs.

All real application wiring lives under ``src/task_tracker``.
This file exists so ``python app.py`` still works in interviews or quick demos.
"""

from __future__ import annotations

import os

import uvicorn

from task_tracker.app import app, create_app

__all__ = ["app", "create_app"]


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "task_tracker.app:app",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        reload=os.environ.get("RELOAD", "1") == "1",
    )
