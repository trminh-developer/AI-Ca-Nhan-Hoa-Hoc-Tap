"""
Zone of Proximal Development (ZPD) & Bloom's Taxonomy Recommender Service (Python 3.14.x).
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Question, Topic
from app.models.interaction import Interaction, LearnerMastery, SpacedRepetition
from app.models.user import User
from app.services.elo_service import elo_service

BLOOM_LABELS: dict[int, str] = {
    1: "Nhớ (Remember)",
    2: "Hiểu (Understand)",
    3: "Áp dụng (Apply)",
    4: "Phân tích (Analyze)",
    5: "Đánh giá (Evaluate)",
    6: "Sáng tạo (Create)",
}

ZPD_LOWER_PROB: float = 0.60
ZPD_UPPER_PROB: float = 0.75
BLOOM_MASTERY_PREREQUISITE: float = 0.70


class ZPDService:
    """Service khuyến nghị nội dung học tập theo vùng ZPD, Bloom's Taxonomy và SM-2."""

    ZPD_LOW_PROB: float = ZPD_LOWER_PROB
    ZPD_HIGH_PROB: float = ZPD_UPPER_PROB
    TARGET_PROB: float = 0.675
    TOO_EASY_PROB: float = 0.85
    TOO_HARD_PROB: float = 0.40
    BLOOM_MASTERY_THRESHOLD: float = BLOOM_MASTERY_PREREQUISITE

    def get_zpd_elo_bounds(self, learner_elo: float) -> tuple[float, float]:
        """Trả về khoảng độ khó Elo [R_L - 85, R_L + 170]."""
        return round(learner_elo - 85.0, 2), round(learner_elo + 170.0, 2)

    def is_in_zpd(self, learner_elo: float, item_difficulty: float) -> bool:
        """Kiểm tra câu hỏi có nằm trong vùng ZPD chuẩn (0.60 <= E_L <= 0.75) hay không."""
        expected = elo_service.calculate_expected_score(learner_elo, item_difficulty)
        return self.ZPD_LOW_PROB <= expected <= self.ZPD_HIGH_PROB

    def is_bloom_level_unlocked(
        self,
        target_bloom_level: int,
        bloom_mastery_map: dict[int, float],
        threshold: float | None = None,
    ) -> bool:
        """Bậc 1 luôn mở; bậc k >= 2 yêu cầu Mastery Score bậc k-1 >= 0.70."""
        required = self.BLOOM_MASTERY_THRESHOLD if threshold is None else float(threshold)
        level = max(1, min(6, int(target_bloom_level)))
        if level == 1:
            return True
        prev_mastery = float(bloom_mastery_map.get(level - 1, 0.0))
        return prev_mastery >= required

    def get_unlocked_bloom_levels(
        self,
        bloom_mastery_map: dict[int, float],
        threshold: float | None = None,
    ) -> list[int]:
        """Trả về danh sách các bậc nhận thức Bloom đã được mở khóa tuần tự."""
        unlocked = [1]
        for level in range(2, 7):
            if self.is_bloom_level_unlocked(level, bloom_mastery_map, threshold):
                unlocked.append(level)
            else:
                break
        return unlocked

    def compute_user_bloom_mastery(self, db: Session, user_id: int) -> dict[int, float]:
        """Tính điểm thành thạo trung bình ở từng bậc Bloom (1..6) của học viên."""
        masteries = (
            db.query(LearnerMastery, Topic.bloom_level)
            .join(Topic, Topic.id == LearnerMastery.topic_id)
            .filter(LearnerMastery.user_id == user_id)
            .all()
        )
        buckets: dict[int, list[float]] = {lvl: [] for lvl in range(1, 7)}
        for mastery, bloom_lvl in masteries:
            lvl = max(1, min(6, int(bloom_lvl or 1)))
            buckets[lvl].append(float(mastery.mastery_score))

        return {
            lvl: (sum(scores) / len(scores) if scores else 0.0)
            for lvl, scores in buckets.items()
        }

    def get_review_questions(
        self,
        db: Session,
        user_id: int,
        topic_id: int | None = None,
        limit: int = 20,
    ) -> list[Question]:
        """Lấy danh sách câu hỏi đến hạn ôn tập SM-2 (next_review <= hiện tại)."""
        now = datetime.now(timezone.utc)
        query = (
            db.query(Question)
            .join(SpacedRepetition, SpacedRepetition.question_id == Question.id)
            .filter(
                SpacedRepetition.user_id == user_id,
                SpacedRepetition.next_review <= now,
            )
        )
        if topic_id is not None:
            query = query.filter(Question.topic_id == topic_id)
        return query.order_by(SpacedRepetition.next_review.asc()).limit(limit).all()

    def get_next_question(
        self,
        db: Session,
        user_id: int,
        topic_id: int | None = None,
    ) -> Question | None:
        """Chọn câu hỏi tối ưu tiếp theo theo SM-2 -> Bloom -> ZPD."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        review_due = self.get_review_questions(db, user_id, topic_id, limit=1)
        if review_due:
            return review_due[0]

        if topic_id is not None:
            mastery = (
                db.query(LearnerMastery)
                .filter(
                    LearnerMastery.user_id == user_id,
                    LearnerMastery.topic_id == topic_id,
                )
                .first()
            )
            learner_elo = mastery.elo_rating if mastery else user.overall_elo
        else:
            learner_elo = user.overall_elo

        recent_stmt = (
            select(Interaction.question_id)
            .where(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .limit(20)
        )

        query = db.query(Question).filter(Question.id.notin_(recent_stmt))
        if topic_id is not None:
            query = query.filter(Question.topic_id == topic_id)
        candidates = query.all()

        if not candidates:
            fallback_query = db.query(Question)
            if topic_id is not None:
                fallback_query = fallback_query.filter(Question.topic_id == topic_id)
            candidates = fallback_query.all()

        if not candidates:
            return None

        max_unlocked = get_unlocked_bloom_level(db, user_id, topic_id)
        bloom_filtered = [q for q in candidates if (q.bloom_level or 1) <= max_unlocked]
        active_pool = bloom_filtered if bloom_filtered else candidates

        optimal = elo_service.select_optimal_content(
            learner_elo=learner_elo,
            available_items=active_pool,
            target_success=self.TARGET_PROB,
            zpd_low=self.ZPD_LOW_PROB,
            zpd_high=self.ZPD_HIGH_PROB,
            max_items=5,
        )
        return optimal[0] if optimal else active_pool[0]

    def get_recommendation_reason(self, learner_elo: float, question: Question) -> str:
        """Sinh lời giải thích khoa học vì sao hệ thống đề xuất câu hỏi này."""
        expected = elo_service.calculate_expected_score(learner_elo, question.difficulty_elo)
        pct = int(round(expected * 100))
        bloom_name = BLOOM_LABELS.get(question.bloom_level, f"Bậc {question.bloom_level}")

        if self.ZPD_LOW_PROB <= expected <= self.ZPD_HIGH_PROB:
            return (
                f"Tối ưu trong vùng ZPD (Xác suất thành công kỳ vọng {pct}%, "
                f"Elo câu hỏi {int(question.difficulty_elo)}, Bloom: {bloom_name})"
            )
        if expected > self.ZPD_HIGH_PROB:
            return (
                f"Củng cố nền tảng (Xác suất thành công kỳ vọng {pct}%, "
                f"Elo câu hỏi {int(question.difficulty_elo)}, Bloom: {bloom_name})"
            )
        return (
            f"Thử thách bứt phá tư duy (Xác suất thành công kỳ vọng {pct}%, "
            f"Elo câu hỏi {int(question.difficulty_elo)}, Bloom: {bloom_name})"
        )


zpd_service = ZPDService()


def get_unlocked_bloom_level(
    db: Session,
    user_id: int,
    topic_id: Optional[int] = None,
) -> int:
    """
    Tính cấp độ Bloom tối đa mà học viên hiện được phép mở khóa:
    Mặc định cấp độ 1-2 luôn mở. Để mở cấp độ k (k >= 3), học viên cần đạt
    Mastery Score >= 0.70 ở cấp độ trước đó.
    """
    if topic_id is not None:
        mastery = (
            db.query(LearnerMastery)
            .filter(
                LearnerMastery.user_id == user_id,
                LearnerMastery.topic_id == topic_id,
            )
            .first()
        )
        if not mastery or mastery.total_attempts == 0:
            return 2
        if mastery.mastery_score >= 0.85:
            return 6
        if mastery.mastery_score >= BLOOM_MASTERY_PREREQUISITE:
            return 4
        return 2

    masteries = (
        db.query(LearnerMastery)
        .filter(LearnerMastery.user_id == user_id)
        .all()
    )
    if not masteries:
        return 2

    max_unlocked = 2
    for level in range(2, 6):
        topics_at_level = (
            db.query(Topic.id).filter(Topic.bloom_level <= level).all()
        )
        topic_ids = {t.id for t in topics_at_level}
        relevant = [m for m in masteries if m.topic_id in topic_ids and m.total_attempts > 0]
        if not relevant:
            break
        avg_mastery = sum(m.mastery_score for m in relevant) / len(relevant)
        if avg_mastery >= BLOOM_MASTERY_PREREQUISITE:
            max_unlocked = level + 1
        else:
            break

    return min(max_unlocked, 6)


def get_next_question(db: Session, user_id: int, topic_id: int | None = None) -> Question | None:
    return zpd_service.get_next_question(db, user_id, topic_id)


def get_review_questions(db: Session, user_id: int, topic_id: int | None = None) -> list[Question]:
    return zpd_service.get_review_questions(db, user_id, topic_id)


def get_recommendation_reason(learner_elo: float, question: Question) -> str:
    return zpd_service.get_recommendation_reason(learner_elo, question)
