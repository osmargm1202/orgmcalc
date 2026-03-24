"""FileAsset model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class FileAsset(Base):
    """FileAsset entity - metadata-driven file storage with polymorphic owner."""

    __tablename__ = "file_assets"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    owner_type: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    original_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    content_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # noqa: UP045
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    storage_bucket: Mapped[str] = mapped_column(Text, nullable=False, default="orgmcalc-uploads")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # noqa: UP045
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    uploaded_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045

    __table_args__ = (
        Index("idx_file_assets_owner", "owner_type", "owner_id"),
        Index("idx_file_assets_storage", "storage_key"),
        Index(
            "idx_file_assets_active_unique",
            "owner_type",
            "owner_id",
            "asset_type",
            postgresql_where=text("is_active = TRUE AND is_deleted = FALSE"),
            unique=True,
        ),
        Index("idx_file_assets_active", "is_active"),
    )
