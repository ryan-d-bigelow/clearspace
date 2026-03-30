"""SQLite + SQLAlchemy access helpers shared across repositories."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """Shared database wrapper.

    Repositories depend on this abstraction rather than constructing engines or
    sessions themselves. This keeps DB configuration centralized and reusable.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.url = f"sqlite:///{path}"
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self._engine = create_engine(self.url, future=True)
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._session_factory

    @contextmanager
    def session(self) -> Iterator[Session]:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
