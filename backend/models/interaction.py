"""
Models Tương tác học tập - Theo dõi quá trình học, mức độ thành thạo và lặp lại ngắt quãng.
"""

from datetime import datetime, date, timezone

from sqlalchemy import (
    Column, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, UniqueConstraint,
)

from database import Base


class Interaction(Base):
    """
    Bảng Tương tác - ghi lại mỗi lần học sinh trả lời câu hỏi.
    
    Attributes:
        id: Khóa chính
        user_id: FK đến người dùng
        question_id: FK đến câu hỏi
        is_correct: Đúng hay sai
        time_spent_ms: Thời gian trả lời (mili giây)
        hints_used: Số gợi ý đã sử dụng
        elo_before: Elo trước khi trả lời
        elo_after: Elo sau khi trả lời
        created_at: Thời điểm tương tác
    """
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

    def __repr__(self):
        return (
            f"<Interaction(user={self.user_id}, question={self.question_id}, "
            f"correct={self.is_correct}, elo_change={self.elo_after - self.elo_before:.1f})>"
        )


class LearnerMastery(Base):
    """
    Bảng Mức độ thành thạo - theo dõi trình độ của học sinh theo từng chủ đề.
    
    Attributes:
        id: Khóa chính
        user_id: FK đến người dùng
        topic_id: FK đến chủ đề
        mastery_score: Điểm thành thạo (0.0 - 1.0)
        elo_rating: Elo riêng cho chủ đề này
        total_attempts: Tổng số lần thử
        correct_attempts: Số lần trả lời đúng
        last_practiced: Lần luyện tập gần nhất
    """
    __tablename__ = "learner_mastery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0, nullable=False)  # 0.0 đến 1.0
    elo_rating = Column(Float, default=1500.0, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    last_practiced = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    # Ràng buộc: mỗi cặp (user_id, topic_id) là duy nhất
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )

    def __repr__(self):
        return (
            f"<LearnerMastery(user={self.user_id}, topic={self.topic_id}, "
            f"mastery={self.mastery_score:.2f}, elo={self.elo_rating:.0f})>"
        )


class SpacedRepetition(Base):
    """
    Bảng Lặp lại ngắt quãng (SM-2) - quản lý lịch ôn tập cho mỗi câu hỏi.
    
    Attributes:
        id: Khóa chính
        user_id: FK đến người dùng
        question_id: FK đến câu hỏi
        easiness_factor: Hệ số dễ (mặc định 2.5, tối thiểu 1.3)
        interval_days: Khoảng cách ôn tập (ngày)
        repetitions: Số lần ôn tập thành công liên tiếp
        next_review: Ngày ôn tập tiếp theo
    """
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

    # Ràng buộc: mỗi cặp (user_id, question_id) là duy nhất
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )

    def __repr__(self):
        return (
            f"<SpacedRepetition(user={self.user_id}, question={self.question_id}, "
            f"EF={self.easiness_factor:.2f}, interval={self.interval_days}d, "
            f"next={self.next_review})>"
        )
