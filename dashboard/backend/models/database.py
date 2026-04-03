# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""SQLAlchemy async database setup with SQLite backend.

The database file lives at ``~/.trusteval/trusteval.db`` so it persists
across project directories while remaining user-scoped.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Database path
# ---------------------------------------------------------------------------

_DB_DIR = Path.home() / ".trusteval"
_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _DB_DIR / "trusteval.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# ---------------------------------------------------------------------------
# Engine & session
# ---------------------------------------------------------------------------

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session for FastAPI dependency injection.

    Yields:
        An ``AsyncSession`` that is automatically closed after use.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

class Evaluation(Base):
    """Persistent record of an LLM evaluation run."""

    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True)
    provider = Column(String(64), nullable=False, index=True)
    model = Column(String(128), nullable=False, index=True)
    industry = Column(String(64), nullable=False, index=True)
    pillars = Column(Text, nullable=False, default="[]")  # JSON list
    status = Column(String(20), nullable=False, default="pending", index=True)
    scores = Column(Text, nullable=False, default="{}")  # JSON dict
    summary = Column(Text, nullable=True)
    config = Column(Text, nullable=False, default="{}")  # JSON dict
    error_message = Column(Text, nullable=True)
    estimated_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # -- helpers for JSON columns ------------------------------------------

    def get_pillars(self) -> list[str]:
        """Deserialise the pillars JSON column."""
        try:
            return json.loads(self.pillars)  # type: ignore[arg-type]
        except (TypeError, json.JSONDecodeError):
            return []

    def set_pillars(self, value: list[str]) -> None:
        """Serialise a list into the pillars column."""
        self.pillars = json.dumps(value)

    def get_scores(self) -> dict:
        """Deserialise the scores JSON column."""
        try:
            return json.loads(self.scores)  # type: ignore[arg-type]
        except (TypeError, json.JSONDecodeError):
            return {}

    def set_scores(self, value: dict) -> None:
        """Serialise a dict into the scores column."""
        self.scores = json.dumps(value)

    def get_config(self) -> dict:
        """Deserialise the config JSON column."""
        try:
            return json.loads(self.config)  # type: ignore[arg-type]
        except (TypeError, json.JSONDecodeError):
            return {}

    def set_config(self, value: dict) -> None:
        """Serialise a dict into the config column."""
        self.config = json.dumps(value)


class Report(Base):
    """Persistent record of a generated report."""

    __tablename__ = "reports"

    id = Column(String(36), primary_key=True)
    evaluation_id = Column(String(36), nullable=False, index=True)
    format = Column(String(10), nullable=False, default="pdf")
    title = Column(String(256), nullable=True)
    file_path = Column(Text, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())


# ---------------------------------------------------------------------------
# Table creation helper
# ---------------------------------------------------------------------------

async def create_tables() -> None:
    """Create all tables if they do not already exist.

    Safe to call on every application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """Gracefully close the async engine connection pool."""
    await engine.dispose()
