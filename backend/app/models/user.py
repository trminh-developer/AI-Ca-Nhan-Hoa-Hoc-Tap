"""
Models Người dùng, Phiên Refresh Token và Cấu hình Hệ thống (Python 3.14.x).
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """Bảng người dùng (RBAC: student, teacher, admin) và điểm năng lực Elo tổng thể."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    overall_elo = Column(Float, default=1500.0, nullable=False)
    role = Column(String(20), default="student", nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    students = relationship("User", backref="teacher", remote_side=[id])
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', elo={self.overall_elo})>"


class RefreshToken(Base):
    """Bảng lưu trữ Refresh Token băm SHA-256 phục vụ Refresh Token Rotation & Logout Revocation."""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_refresh_tokens_user_revoked", "user_id", "revoked"),
    )


class SystemConfig(Base):
    """Bảng lưu cấu hình động của thuật toán thích ứng (K-factor, ZPD bounds) dành cho Admin."""

    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
