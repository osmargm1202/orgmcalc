"""File assets repository - metadata CRUD with single-active semantics."""
from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class FilesRepository:
    """Repository for file_assets metadata operations."""

    @staticmethod
    async def get_active(
        owner_type: str, owner_id: int, asset_type: str
    ) -> dict[str, Any] | None:
        """Get active file for owner+type."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, owner_type, owner_id, asset_type, filename,
                           original_name, content_type, size_bytes, storage_key,
                           storage_bucket, is_active, created_at::text, updated_at::text
                    FROM file_assets
                    WHERE owner_type = %s AND owner_id = %s AND asset_type = %s
                      AND is_active = TRUE AND is_deleted = FALSE
                    LIMIT 1
                    """,
                    (owner_type, owner_id, asset_type),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def list_by_owner(
        owner_type: str, owner_id: int
    ) -> list[dict[str, Any]]:
        """List all active files for an owner."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, owner_type, owner_id, asset_type, filename,
                           original_name, content_type, size_bytes, storage_key,
                           storage_bucket, is_active, created_at::text, updated_at::text
                    FROM file_assets
                    WHERE owner_type = %s AND owner_id = %s AND is_active = TRUE
                      AND is_deleted = FALSE
                    ORDER BY asset_type
                    """,
                    (owner_type, owner_id),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def create_or_replace(
        owner_type: str,
        owner_id: int,
        asset_type: str,
        filename: str,
        storage_key: str,
        storage_bucket: str,
        original_name: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
    ) -> dict[str, Any]:
        """Create or replace file (single-active semantics)."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                # Deactivate existing
                await cur.execute(
                    """
                    UPDATE file_assets
                    SET is_active = FALSE, is_deleted = TRUE, deleted_at = now()
                    WHERE owner_type = %s AND owner_id = %s AND asset_type = %s
                      AND is_active = TRUE AND is_deleted = FALSE
                    """,
                    (owner_type, owner_id, asset_type),
                )
                # Create new
                await cur.execute(
                    """
                    INSERT INTO file_assets (
                        owner_type, owner_id, asset_type, filename, original_name,
                        content_type, size_bytes, storage_key, storage_bucket
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, owner_type, owner_id, asset_type, filename,
                              original_name, content_type, size_bytes, storage_key,
                              storage_bucket, is_active, created_at::text, updated_at::text
                    """,
                    (
                        owner_type, owner_id, asset_type, filename, original_name,
                        content_type, size_bytes, storage_key, storage_bucket
                    ),
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def deactivate(
        owner_type: str, owner_id: int, asset_type: str
    ) -> bool:
        """Deactivate (soft delete) file. Returns True if found."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE file_assets
                    SET is_active = FALSE, is_deleted = TRUE, deleted_at = now()
                    WHERE owner_type = %s AND owner_id = %s AND asset_type = %s
                      AND is_active = TRUE AND is_deleted = FALSE
                    RETURNING id
                    """,
                    (owner_type, owner_id, asset_type),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def get_by_storage_key(storage_key: str) -> dict[str, Any] | None:
        """Get file by storage key."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, owner_type, owner_id, asset_type, filename,
                           original_name, content_type, size_bytes, storage_key,
                           storage_bucket, is_active, created_at::text, updated_at::text
                    FROM file_assets
                    WHERE storage_key = %s AND is_deleted = FALSE
                    LIMIT 1
                    """,
                    (storage_key,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def get_batch_status(storage_keys: list[str]) -> dict[str, dict[str, Any]]:
        """Get status for multiple storage keys."""
        if not storage_keys:
            return {}
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT storage_key, filename, original_name, content_type,
                           size_bytes, is_active
                    FROM file_assets
                    WHERE storage_key = ANY(%s) AND is_deleted = FALSE
                    """,
                    (storage_keys,),
                )
                rows = await cur.fetchall()
                result = {}
                for row in rows:
                    result[row[0]] = {
                        "available": row[5],  # is_active
                        "filename": row[1],
                        "original_name": row[2],
                        "content_type": row[3],
                        "size_bytes": row[4],
                    }
                return result
