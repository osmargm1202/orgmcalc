"""Authentication repository - database operations for auth."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload

from orgmcalc.db.session import get_session
from orgmcalc.models import AuthSession, AuthUser


def _user_to_dict(user: AuthUser) -> dict[str, Any]:
    """Convert AuthUser model to dict with formatted timestamps."""
    return {
        "id": str(user.id),
        "google_id": user.google_id,
        "email": user.email,
        "name": user.name,
        "given_name": user.given_name,
        "family_name": user.family_name,
        "picture": user.picture,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def _session_to_dict(session: AuthSession, include_user: bool = False) -> dict[str, Any]:
    """Convert AuthSession model to dict."""
    result: dict[str, Any] = {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "token_hash": session.token_hash,
        "expires_at": session.expires_at.isoformat() if session.expires_at else None,
        "revoked": session.revoked,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }
    if include_user and session.user is not None:
        result["user"] = {
            "id": str(session.user.id),
            "email": session.user.email,
            "name": session.user.name,
            "picture": session.user.picture,
        }
    return result


class AuthRepository:
    """Repository for authentication-related database operations."""

    @staticmethod
    async def get_user_by_google_id(google_id: str) -> dict[str, Any] | None:
        """Get user by Google ID."""
        async with get_session() as session:
            result = await session.execute(
                select(AuthUser).where(
                    and_(
                        AuthUser.google_id == google_id,
                        AuthUser.is_active,
                    )
                )
            )
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return _user_to_dict(user)

    @staticmethod
    async def get_user_by_id(user_id: str) -> dict[str, Any] | None:
        """Get user by internal ID."""
        async with get_session() as session:
            result = await session.execute(
                select(AuthUser).where(
                    and_(
                        AuthUser.id == UUID(user_id),
                        AuthUser.is_active,
                    )
                )
            )
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return _user_to_dict(user)

    @staticmethod
    async def create_or_update_user(
        google_id: str,
        email: str,
        name: str | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        picture: str | None = None,
    ) -> dict[str, Any]:
        """Create or update a user from Google OAuth data."""
        async with get_session() as session:
            result = await session.execute(select(AuthUser).where(AuthUser.google_id == google_id))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                existing_user.email = email
                existing_user.name = name
                existing_user.given_name = given_name
                existing_user.family_name = family_name
                existing_user.picture = picture
                existing_user.updated_at = datetime.now(UTC)
                await session.flush()
                await session.refresh(existing_user)
                return _user_to_dict(existing_user)
            else:
                new_user = AuthUser(
                    google_id=google_id,
                    email=email,
                    name=name,
                    given_name=given_name,
                    family_name=family_name,
                    picture=picture,
                )
                session.add(new_user)
                await session.flush()
                await session.refresh(new_user)
                return _user_to_dict(new_user)

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    async def create_session(
        user_id: str,
        token: str,
        expires_in_seconds: int = 86400,
    ) -> dict[str, Any]:
        """Create a new session."""
        token_hash = AuthRepository._hash_token(token)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)

        async with get_session() as session:
            new_session = AuthSession(
                user_id=UUID(user_id),
                token_hash=token_hash,
                expires_at=expires_at,
            )
            session.add(new_session)
            await session.flush()
            await session.refresh(new_session)
            return _session_to_dict(new_session)

    @staticmethod
    async def get_session_by_token(token: str) -> dict[str, Any] | None:
        """Get valid session by token."""
        token_hash = AuthRepository._hash_token(token)

        async with get_session() as session:
            result = await session.execute(
                select(AuthSession)
                .options(selectinload(AuthSession.user))
                .join(AuthUser, AuthSession.user_id == AuthUser.id)
                .where(
                    and_(
                        AuthSession.token_hash == token_hash,
                        AuthSession.expires_at > datetime.now(UTC),
                        not AuthSession.revoked,  # type: ignore[arg-type]
                        AuthUser.is_active,
                    )
                )
            )
            session_obj = result.scalar_one_or_none()
            if session_obj is None:
                return None
            return _session_to_dict(session_obj, include_user=True)

    @staticmethod
    async def revoke_session(token: str) -> bool:
        """Revoke a session by token."""
        token_hash = AuthRepository._hash_token(token)

        async with get_session() as session:
            result = await session.execute(
                select(AuthSession).where(
                    and_(
                        AuthSession.token_hash == token_hash,
                        not AuthSession.revoked,  # type: ignore[arg-type]
                    )
                )
            )
            session_obj = result.scalar_one_or_none()
            if session_obj is None:
                return False

            session_obj.revoked = True
            session_obj.revoked_at = datetime.now(UTC)
            await session.flush()
            return True

    @staticmethod
    async def update_last_used(token: str) -> None:
        """Update last used timestamp for a session."""
        token_hash = AuthRepository._hash_token(token)

        async with get_session() as session:
            await session.execute(
                update(AuthSession)
                .where(AuthSession.token_hash == token_hash)
                .values(last_used_at=datetime.now(UTC))
            )
