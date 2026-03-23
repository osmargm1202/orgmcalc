"""Authentication repository - database operations for auth."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from orgmcalc.db.connection import init_pool


class AuthRepository:
    """Repository for authentication-related database operations."""

    @staticmethod
    async def get_user_by_google_id(google_id: str) -> dict[str, Any] | None:
        """Get user by Google ID."""
        pool = init_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, google_id, email, name, given_name, family_name,
                           picture, is_active, created_at, updated_at
                    FROM auth_users
                    WHERE google_id = %s AND is_active = TRUE
                    """,
                    (google_id,),
                )
                row = await cur.fetchone()
                if row:
                    return {
                        "id": str(row[0]),
                        "google_id": row[1],
                        "email": row[2],
                        "name": row[3],
                        "given_name": row[4],
                        "family_name": row[5],
                        "picture": row[6],
                        "is_active": row[7],
                        "created_at": row[8].isoformat() if row[8] else None,
                        "updated_at": row[9].isoformat() if row[9] else None,
                    }
                return None

    @staticmethod
    async def get_user_by_id(user_id: str) -> dict[str, Any] | None:
        """Get user by internal ID."""
        pool = init_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, google_id, email, name, given_name, family_name,
                           picture, is_active, created_at, updated_at
                    FROM auth_users
                    WHERE id = %s AND is_active = TRUE
                    """,
                    (UUID(user_id),),
                )
                row = await cur.fetchone()
                if row:
                    return {
                        "id": str(row[0]),
                        "google_id": row[1],
                        "email": row[2],
                        "name": row[3],
                        "given_name": row[4],
                        "family_name": row[5],
                        "picture": row[6],
                        "is_active": row[7],
                        "created_at": row[8].isoformat() if row[8] else None,
                        "updated_at": row[9].isoformat() if row[9] else None,
                    }
                return None

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
        pool = init_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO auth_users (google_id, email, name, given_name, family_name, picture)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (google_id) DO UPDATE SET
                        email = EXCLUDED.email,
                        name = EXCLUDED.name,
                        given_name = EXCLUDED.given_name,
                        family_name = EXCLUDED.family_name,
                        picture = EXCLUDED.picture,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id, google_id, email, name, given_name, family_name,
                              picture, is_active, created_at, updated_at
                    """,
                    (google_id, email, name, given_name, family_name, picture),
                )
                row = await cur.fetchone()
                await conn.commit()
                return {
                    "id": str(row[0]),
                    "google_id": row[1],
                    "email": row[2],
                    "name": row[3],
                    "given_name": row[4],
                    "family_name": row[5],
                    "picture": row[6],
                    "is_active": row[7],
                    "created_at": row[8].isoformat() if row[8] else None,
                    "updated_at": row[9].isoformat() if row[9] else None,
                }

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
        pool = init_pool()
        token_hash = AuthRepository._hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO auth_sessions (user_id, token_hash, expires_at)
                    VALUES (%s, %s, %s)
                    RETURNING id, user_id, token_hash, expires_at, revoked, created_at
                    """,
                    (UUID(user_id), token_hash, expires_at),
                )
                row = await cur.fetchone()
                await conn.commit()
                return {
                    "id": str(row[0]),
                    "user_id": str(row[1]),
                    "token_hash": row[2],
                    "expires_at": row[3].isoformat() if row[3] else None,
                    "revoked": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                }

    @staticmethod
    async def get_session_by_token(token: str) -> dict[str, Any] | None:
        """Get valid session by token."""
        pool = init_pool()
        token_hash = AuthRepository._hash_token(token)

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT s.id, s.user_id, s.expires_at, s.revoked, s.created_at,
                           u.email, u.name, u.picture
                    FROM auth_sessions s
                    JOIN auth_users u ON s.user_id = u.id
                    WHERE s.token_hash = %s
                      AND s.expires_at > CURRENT_TIMESTAMP
                      AND s.revoked = FALSE
                      AND u.is_active = TRUE
                    """,
                    (token_hash,),
                )
                row = await cur.fetchone()
                if row:
                    return {
                        "id": str(row[0]),
                        "user_id": str(row[1]),
                        "expires_at": row[2].isoformat() if row[2] else None,
                        "revoked": row[3],
                        "created_at": row[4].isoformat() if row[4] else None,
                        "user": {
                            "id": str(row[1]),
                            "email": row[5],
                            "name": row[6],
                            "picture": row[7],
                        },
                    }
                return None

    @staticmethod
    async def revoke_session(token: str) -> bool:
        """Revoke a session by token."""
        pool = init_pool()
        token_hash = AuthRepository._hash_token(token)

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE auth_sessions
                    SET revoked = TRUE, revoked_at = CURRENT_TIMESTAMP
                    WHERE token_hash = %s AND revoked = FALSE
                    RETURNING id
                    """,
                    (token_hash,),
                )
                row = await cur.fetchone()
                await conn.commit()
                return row is not None

    @staticmethod
    async def update_last_used(token: str) -> None:
        """Update last used timestamp for a session."""
        pool = init_pool()
        token_hash = AuthRepository._hash_token(token)

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE auth_sessions
                    SET last_used_at = CURRENT_TIMESTAMP
                    WHERE token_hash = %s
                    """,
                    (token_hash,),
                )
                await conn.commit()
