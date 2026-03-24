"""Auth models - AuthUser and AuthSession."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class AuthUser(Base):
    """AuthUser entity - normalized Google OAuth user."""

    __tablename__ = "auth_users"

    id: Mapped[str] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # noqa: UP045
    given_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # noqa: UP045
    family_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # noqa: UP045
    picture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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

    sessions: Mapped[list["AuthSession"]] = relationship(  # noqa: F821  # type: ignore[name-defined]
        "AuthSession", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_auth_users_google_id", "google_id"),
        Index("idx_auth_users_email", "email"),
    )


class AuthSession(Base):
    """AuthSession entity - bearer token sessions for authentication."""

    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(
        Uuid,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[str] = mapped_column(
        Uuid,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # noqa: UP045
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # noqa: UP045
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(  # noqa: UP045
        String(255), unique=True, nullable=True
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    max_inactive_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    user: Mapped["AuthUser"] = relationship("AuthUser", back_populates="sessions")  # noqa: F821  # type: ignore[name-defined]

    __table_args__ = (
        Index("idx_auth_sessions_token_hash", "token_hash"),
        Index("idx_auth_sessions_user_id", "user_id"),
        Index("idx_auth_sessions_refresh_token", "refresh_token_hash"),
        Index("idx_auth_sessions_expires_at", "expires_at"),
    )
