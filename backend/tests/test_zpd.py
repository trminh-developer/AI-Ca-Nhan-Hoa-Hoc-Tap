"""
Unit Tests cho ZPD Recommender & Ràng buộc Tiên quyết Thang đo Nhận thức Bloom (6 cấp độ).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.content import Question, Subject, Topic
from app.models.interaction import LearnerMastery, SpacedRepetition
from app.models.user import User
from app.services.zpd_service import (
    BLOOM_MASTERY_PREREQUISITE,
    get_next_question,
    get_recommendation_reason,
    get_unlocked_bloom_level,
)


def _create_in_memory_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_bloom_prerequisite_unlocking():
    """
    Ràng buộc tiên quyết Bloom:
    Học viên không được mở khóa cấp độ k nếu chưa đạt Mastery >= 0.70 ở cấp độ k-1.
    """
    db = _create_in_memory_db()
    user = User(username="bloom_tester", email="b@test.com", hashed_password="x", overall_elo=1500.0)
    subj = Subject(name="Test Subject")
    db.add_all([user, subj])
    db.flush()

    t1 = Topic(subject_id=subj.id, name="T1", bloom_level=1, order_index=1)
    t2 = Topic(subject_id=subj.id, name="T2", bloom_level=2, order_index=2)
    db.add_all([t1, t2])
    db.flush()

    # Khi chưa có lịch sử -> Mặc định cho phép cấp độ 1-2
    assert get_unlocked_bloom_level(db, user.id, topic_id=t1.id) == 2

    # Khi đạt Mastery 0.50 (< 0.70) ở Topic 1 (Bloom 1) -> Không mở khóa cao hơn
    m1 = LearnerMastery(
        user_id=user.id,
        topic_id=t1.id,
        mastery_score=0.50,
        elo_rating=1450.0,
        total_attempts=4,
        correct_attempts=2,
    )
    db.add(m1)
    db.commit()
    assert get_unlocked_bloom_level(db, user.id, topic_id=t1.id) == 2

    # Khi nâng Mastery lên 0.80 (>= 0.70) ở Topic 1 và Topic 2 -> Mở khóa cấp tiếp theo
    m1.mastery_score = 0.80
    m2 = LearnerMastery(
        user_id=user.id,
        topic_id=t2.id,
        mastery_score=0.75,
        elo_rating=1550.0,
        total_attempts=4,
        correct_attempts=3,
    )
    db.add(m2)
    db.commit()
    assert BLOOM_MASTERY_PREREQUISITE == 0.70
    assert get_unlocked_bloom_level(db, user.id) >= 3
    db.close()


def test_zpd_prioritizes_due_spaced_repetition():
    """Nếu có câu hỏi đến hạn ôn tập SM-2 (next_review <= now), hệ thống phải ưu tiên trả về trước."""
    db = _create_in_memory_db()
    user = User(username="sr_tester", email="sr@test.com", hashed_password="x", overall_elo=1500.0)
    subj = Subject(name="Toán")
    db.add_all([user, subj])
    db.flush()

    topic = Topic(subject_id=subj.id, name="Đại số", bloom_level=1)
    db.add(topic)
    db.flush()

    q_due = Question(
        topic_id=topic.id,
        question_text="Câu đến hạn SM-2",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D",
        correct_answer="a",
        difficulty_elo=1100.0,
        bloom_level=1,
    )
    q_zpd = Question(
        topic_id=topic.id,
        question_text="Câu mới trong ZPD",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D",
        correct_answer="b",
        difficulty_elo=1450.0,
        bloom_level=1,
    )
    db.add_all([q_due, q_zpd])
    db.flush()

    sr = SpacedRepetition(
        user_id=user.id,
        question_id=q_due.id,
        easiness_factor=2.5,
        interval_days=1,
        repetitions=1,
        next_review=datetime.now(timezone.utc) - timedelta(hours=2),
    )
    db.add(sr)
    db.commit()

    rec = get_next_question(db, user.id, topic_id=topic.id)
    assert rec is not None
    assert rec.id == q_due.id
    reason = get_recommendation_reason(1500.0, rec)
    assert "Nhớ" in reason or "Elo" in reason
    db.close()
