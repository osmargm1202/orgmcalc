"""FastAPI dependencies including authentication."""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg import AsyncConnection

from orgmcalc.config import Settings, get_settings
from orgmcalc.db.connection import get_async_connection
from orgmcalc.services.auth import AuthService


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    """Dependency to get database connection."""
    async with get_async_connection() as conn:
        yield conn


async def get_settings_dep() -> Settings:
    """Dependency to get application settings."""
    return get_settings()


# Type annotations for dependency injection
DBDep = Annotated[AsyncConnection, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


# Authentication scheme
security = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any]:
    """Dependency to require authentication.

    Use this for POST, PATCH, DELETE endpoints that require authentication.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dictionary with user info

    Raises:
        HTTPException: 401 if no valid token provided
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user = await AuthService.get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def optional_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any] | None:
    """Dependency for optional authentication.

    Use this for GET endpoints where auth is optional (for future use).
    Returns None if no valid token, user dict if valid token.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dictionary or None
    """
    if not credentials:
        return None

    token = credentials.credentials
    return await AuthService.get_current_user(token)


# Type annotations for auth dependencies
AuthRequiredDep = Annotated[dict[str, Any], Depends(require_auth)]
AuthOptionalDep = Annotated[dict[str, Any] | None, Depends(optional_auth)]
