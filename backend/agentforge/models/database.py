"""Database engine and session setup (async SQLAlchemy)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from agentforge.config import settings

db_url = settings.database_url
if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite+aiosqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        columns = [
            ("model_name", "VARCHAR(64)"),
            ("error_message", "TEXT"),
            ("result", "JSON"),
        ]
        for col_name, col_type in columns:
            try:
                await conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type};"))
            except Exception:
                pass


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        yield session

