"""Test fixtures and configuration."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from orgmcalc.api.app import create_app
from orgmcalc.config import Settings, get_settings
from orgmcalc.db.connection import close_pool, init_pool


# Test database URL - uses test database
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/orgmcalc_test"


def get_test_settings() -> Settings:
    """Return test settings."""
    return Settings(
        base_url="http://testserver",
        database_url=TEST_DATABASE_URL,  # type: ignore[arg-type]
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        r2_endpoint_url="",
        r2_access_key_id="",
        r2_secret_access_key="",
        r2_bucket_name="test-bucket",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_app() -> AsyncGenerator[FastAPI, None]:
    """Create test application with overridden dependencies."""
    app = create_app()
    
    # Override settings dependency
    app.dependency_overrides[get_settings] = get_test_settings
    
    yield app
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def mock_storage() -> AsyncGenerator[MagicMock, None]:
    """Mock storage service for tests."""
    with patch("orgmcalc.storage.object_store.ObjectStore") as mock_store_class:
        mock_store = MagicMock()
        mock_store.upload_file = AsyncMock(return_value={
            "key": "test/key",
            "url": "https://test.example.com/test/key",
        })
        mock_store.get_download_url = AsyncMock(return_value="https://test.example.com/download")
        mock_store.delete_file = AsyncMock(return_value=True)
        mock_store_class.return_value = mock_store
        yield mock_store


@pytest.fixture
def mock_auth_service() -> Generator[MagicMock, None, None]:
    """Mock auth service for tests."""
    with patch("orgmcalc.api.dependencies.AuthService") as mock_service:
        mock_service.get_current_user = AsyncMock(return_value={
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
        })
        mock_service.validate_session = AsyncMock(return_value={
            "id": "test-session-id",
            "user_id": "test-user-id",
            "user": {
                "id": "test-user-id",
                "email": "test@example.com",
                "name": "Test User",
            }
        })
        yield mock_service


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Return authorization headers for authenticated requests."""
    return {"Authorization": "Bearer test-token"}


class MockAsyncCursor:
    """Mock async cursor for database operations."""
    
    def __init__(self, fetchone_result: Any = None, fetchall_result: list[Any] | None = None):
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result or []
        self.executed_queries: list[tuple[str, tuple]] = []
    
    async def execute(self, query: str, params: tuple = ()) -> None:
        self.executed_queries.append((query, params))
    
    async def fetchone(self) -> Any:
        return self.fetchone_result
    
    async def fetchall(self) -> list[Any]:
        return self.fetchall_result
    
    async def __aenter__(self) -> "MockAsyncCursor":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        pass


class MockAsyncConnection:
    """Mock async connection for database operations."""
    
    def __init__(self, cursor: MockAsyncCursor | None = None):
        self.cursor = cursor or MockAsyncCursor()
        self.committed = False
        self.rolled_back = False
    
    def cursor(self, *args: Any, **kwargs: Any) -> MockAsyncCursor:
        return self.cursor
    
    async def commit(self) -> None:
        self.committed = True
    
    async def rollback(self) -> None:
        self.rolled_back = True
    
    async def __aenter__(self) -> "MockAsyncConnection":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.fixture
def mock_db_connection() -> MockAsyncConnection:
    """Create a mock database connection."""
    return MockAsyncConnection()
