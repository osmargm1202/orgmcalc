"""File assets repository - metadata CRUD with single-active semantics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, select, update

from orgmcalc.db.session import get_session
from orgmcalc.models import FileAsset


def _file_asset_to_dict(file_asset: FileAsset) -> dict[str, Any]:
    """Convert FileAsset model to dict with formatted timestamps."""
    return {
        c.name: (
            getattr(file_asset, c.name).isoformat()
            if hasattr(getattr(file_asset, c.name), "isoformat")
            else getattr(file_asset, c.name)
        )
        for c in file_asset.__table__.columns
    }


class FilesRepository:
    """Repository for file_assets metadata operations."""

    @staticmethod
    async def get_active(owner_type: str, owner_id: str, asset_type: str) -> dict[str, Any] | None:
        """Get active file for owner+type."""
        async with get_session() as session:
            result = await session.execute(
                select(FileAsset).where(
                    and_(
                        FileAsset.owner_type == owner_type,
                        FileAsset.owner_id == owner_id,
                        FileAsset.asset_type == asset_type,
                        FileAsset.is_active,  # noqa: E712
                        ~FileAsset.is_deleted,
                    )
                )
            )
            file_asset = result.scalar_one_or_none()
            if file_asset is None:
                return None
            return _file_asset_to_dict(file_asset)

    @staticmethod
    async def create_or_replace(
        owner_type: str,
        owner_id: str,
        asset_type: str,
        filename: str,
        storage_key: str,
        storage_bucket: str,
        original_name: str | None = None,
        content_type: str | None = None,
        size_bytes: int | None = None,
    ) -> dict[str, Any]:
        """Create or replace file (single-active semantics)."""
        async with get_session() as session:
            await session.execute(
                update(FileAsset)
                .where(
                    and_(
                        FileAsset.owner_type == owner_type,
                        FileAsset.owner_id == owner_id,
                        FileAsset.asset_type == asset_type,
                        FileAsset.is_active,  # noqa: E712
                        ~FileAsset.is_deleted,
                    )
                )
                .values(is_active=False, is_deleted=True, deleted_at=datetime.utcnow())
            )

            new_file = FileAsset(
                owner_type=owner_type,
                owner_id=owner_id,
                asset_type=asset_type,
                filename=filename,
                original_name=original_name,
                content_type=content_type,
                size_bytes=size_bytes,
                storage_key=storage_key,
                storage_bucket=storage_bucket,
                is_active=True,
                is_deleted=False,
            )
            session.add(new_file)
            await session.flush()
            await session.refresh(new_file)
            return _file_asset_to_dict(new_file)

    @staticmethod
    async def get_batch_status(storage_keys: list[str]) -> dict[str, dict[str, Any]]:
        """Get status for multiple storage keys."""
        if not storage_keys:
            return {}
        async with get_session() as session:
            result = await session.execute(
                select(FileAsset).where(
                    and_(
                        FileAsset.storage_key.in_(storage_keys),
                        ~FileAsset.is_deleted,
                    )
                )
            )
            file_assets = result.scalars().all()
            return {
                fa.storage_key: {
                    "available": fa.is_active,
                    "filename": fa.filename,
                    "original_name": fa.original_name,
                    "content_type": fa.content_type,
                    "size_bytes": fa.size_bytes,
                }
                for fa in file_assets
            }
