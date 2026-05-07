"""SQLAlchemy async session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from orgmcalc.config import get_settings

settings = get_settings()


def _normalize_asyncpg_database_url(database_url: str) -> str:
    """Normalize DATABASE_URL for SQLAlchemy asyncpg engine.

    Converts PostgreSQL URL scheme to ``postgresql+asyncpg`` and maps
    ``sslmode`` query parameter to ``ssl`` (unsupported ``sslmode`` can raise
    ``TypeError: connect() got an unexpected keyword argument 'sslmode'``).
    """

    if database_url.startswith("postgresql://"):
        normalized = database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )
    elif database_url.startswith("postgres://"):
        normalized = database_url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )
    else:
        normalized = database_url

    parts = urlsplit(normalized)
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)

    ssl_value: str | None = None
    has_ssl = False
    filtered_pairs: list[tuple[str, str]] = []

    for key, value in query_pairs:
        if key == "sslmode":
            ssl_value = value
            continue
        if key == "ssl":
            has_ssl = True
        filtered_pairs.append((key, value))

    if ssl_value is not None and not has_ssl:
        filtered_pairs.append(("ssl", ssl_value))

    rebuilt_query = urlencode(filtered_pairs)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, rebuilt_query, parts.fragment))


_async_engine = create_async_engine(
    _normalize_asyncpg_database_url(settings.database_url),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session_maker = async_sessionmaker(
    _async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions."""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
