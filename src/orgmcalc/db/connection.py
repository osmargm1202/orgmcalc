"""Database connection management."""

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

import psycopg
from psycopg import Connection, Cursor
from psycopg_pool import AsyncConnectionPool

from orgmcalc.config import get_settings

_settings = get_settings()


# Sync connection for migrations
def get_sync_connection() -> Connection:
    """Get a synchronous database connection."""
    return psycopg.connect(_settings.database_dsn)


@contextmanager
def sync_cursor() -> Generator[Cursor, None, None]:
    """Context manager for sync database cursor."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    finally:
        conn.close()


# Async connection pool for API requests
_pool: AsyncConnectionPool | None = None


def init_pool() -> AsyncConnectionPool:
    """Initialize the async connection pool."""
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=_settings.database_dsn,
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_pool() -> None:
    """Close the async connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_async_connection() -> AsyncGenerator:
    """Get async connection from pool."""
    pool = init_pool()
    async with pool.connection() as conn:
        yield conn
