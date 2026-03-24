"""Database connection management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import psycopg
from psycopg import Connection
from sqlalchemy.ext.asyncio import AsyncSession

from orgmcalc.config import get_settings
from orgmcalc.db.session import get_session

_settings = get_settings()


def get_sync_connection() -> Connection:
    """Get a synchronous database connection."""
    return psycopg.connect(_settings.database_dsn)


def init_pool() -> None:
    """No-op for compatibility."""
    pass


async def close_pool() -> None:
    """No-op for compatibility."""
    pass


@asynccontextmanager
async def get_async_connection() -> AsyncGenerator[AsyncSession, None]:
    """Get async connection. Delegates to get_session for backwards compatibility."""
    async with get_session() as session:
        yield session
