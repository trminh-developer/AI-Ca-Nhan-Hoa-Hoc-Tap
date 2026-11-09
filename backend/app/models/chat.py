"""Model Lịch sử Hội thoại với Trợ giảng AI Socratic."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text

from app.db.base import Base


class ChatHistory(Base):
    """Bảng lưu lịch sử hội thoại giữa Học viên và Trợ giảng AI."""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # 'user' | 'model'
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_chat_history_user_created", "user_id", "created_at"),
    )
