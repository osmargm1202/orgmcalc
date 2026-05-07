"""FastAPI dependencies including JWKS-backed authentication."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from orgmcalc.config import Settings, get_settings
from orgmcalc.db.connection import get_async_connection
from orgmcalc.services.jwks_verifier import (
    AuthTokenError,
    JwksVerifier,
    VerifiedAccessClaims,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database connection."""
    async with get_async_connection() as conn:
        yield conn


async def get_settings_dep() -> Settings:
    """Dependency to get application settings."""
    return get_settings()


# Type annotations for dependency injection
DBDep = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]


# Authentication scheme
security = HTTPBearer(auto_error=False)
_jwks_verifier: JwksVerifier | None = None


def get_jwks_verifier() -> JwksVerifier:
    """Return the process-local JWKS verifier singleton."""
    global _jwks_verifier
    if _jwks_verifier is None:
        _jwks_verifier = JwksVerifier(get_settings())
    return _jwks_verifier


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> VerifiedAccessClaims:
    """Dependency to require authentication.

    Use this for POST, PATCH, DELETE endpoints that require authentication.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Verified access-token claims

    Raises:
        HTTPException: 401 if no valid token provided
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await get_jwks_verifier().verify_access_token(credentials.credentials)
    except AuthTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# Type annotations for auth dependencies
AuthRequiredDep = Annotated[VerifiedAccessClaims, Depends(require_auth)]
