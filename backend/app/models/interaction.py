"""
Models Tương tác học tập, Mức thành thạo (Mastery) và Lặp lại ngắt quãng (SM-2)
kèm Composite Indexes tối ưu hóa truy vấn.
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)

from app.db.base import Base


class Interaction(Base):
    """Bảng ghi nhận từng lượt trả lời câu hỏi và biến thiên Elo."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False)
    time_spent_ms = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    elo_before = Column(Float, nullable=False)
    elo_after = Column(Float, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_interactions_user_question_created", "user_id", "question_id", "created_at"),
    )


class LearnerMastery(Base):
    """Bảng theo dõi điểm thành thạo (Mastery Score) và Elo riêng theo từng Chủ đề."""

    __tablename__ = "learner_mastery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0, nullable=False)
    elo_rating = Column(Float, default=1500.0, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    last_practiced = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
        Index("ix_learner_mastery_user_topic", "user_id", "topic_id"),
    )


class SpacedRepetition(Base):
    """Bảng quản lý lịch ôn tập lặp lại ngắt quãng SuperMemo-2 (SM-2)."""

    __tablename__ = "spaced_repetition"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    easiness_factor = Column(Float, default=2.5, nullable=False)
    interval_days = Column(Integer, default=1, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    next_review = Column(
        Date,
        default=lambda: date.today(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question"),
        Index("ix_spaced_repetition_user_next_review", "user_id", "next_review"),
    )
