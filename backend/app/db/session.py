from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from ..core.config import settings

# Ensure model modules are imported so Base.metadata is populated
from app.db import models  # noqa: F401
from app.services.users import ensure_seed_users

_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[sessionmaker] = None


def get_engine() -> AsyncEngine:
    global _engine, _async_session_maker
    if _engine is None:
        _engine = create_async_engine(settings.POSTGRES_DSN, echo=False, pool_pre_ping=True)
        _async_session_maker = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine


def async_session() -> AsyncSession:
    global _async_session_maker
    if _async_session_maker is None:
        get_engine()
    assert _async_session_maker is not None
    return _async_session_maker()

async def init_db():
    engine = get_engine()
    # Alembic migrations are the source of truth. Ensure schema is applied before startup.
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'users'"
            )
        )
        if result.first() is None:
            raise RuntimeError(
                "Database schema is not initialized. Run `alembic upgrade head` before starting the app."
            )

    # Seed default users (admin/analyst/viewer) if DB is empty.
    session = async_session()
    try:
        await ensure_seed_users(session)
        await session.commit()
    finally:
        await session.close()
