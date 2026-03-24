"""Database connection management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import psycopg
from psycopg import AsyncConnection, Connection

from orgmcalc.config import get_settings

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
async def get_async_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Get async connection. Creates new connection per request for Neon compatibility."""
    conn = await psycopg.AsyncConnection.connect(_settings.database_dsn)
    try:
        yield conn
    finally:
        await conn.close()
