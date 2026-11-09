"""
Analytics Service (Python 3.14.x) - Tổng hợp dữ liệu biểu đồ Elo Timeline,
Biểu đồ Radar 6 bậc nhận thức Bloom's Taxonomy và thống kê SM-2.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.content import Question, Subject, Topic
from app.models.interaction import Interaction, LearnerMastery, SpacedRepetition
from app.models.user import User
from app.schemas.learning import (
    BloomRadarPoint,
    EloHistoryPoint,
    LearnerMasteryResponse,
    ProgressResponse,
    TopicMasteryItem,
)
from app.services.zpd_service import BLOOM_LABELS, zpd_service


class AnalyticsService:
    """Service phân tích dữ liệu học tập cho Dashboard học viên và giảng viên."""

    def build_user_progress(self, db: Session, current_user: User) -> ProgressResponse:
        """Tổng hợp toàn bộ chỉ số tiến độ, chuỗi Elo theo thời gian và Bloom Radar."""
        masteries = (
            db.query(LearnerMastery)
            .filter(LearnerMastery.user_id == current_user.id)
            .all()
        )

        topics_mastery: list[TopicMasteryItem] = []
        for m in masteries:
            topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
            if not topic:
                continue
            subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
            accuracy = m.correct_attempts / m.total_attempts if m.total_attempts > 0 else 0.0
            topics_mastery.append(
                TopicMasteryItem(
                    topic_id=m.topic_id,
                    topic_name=topic.name,
                    subject_id=topic.subject_id,
                    subject_name=subject.name if subject else "",
                    bloom_level=topic.bloom_level,
                    mastery_score=round(m.mastery_score, 4),
                    elo_rating=round(m.elo_rating, 2),
                    total_attempts=m.total_attempts,
                    correct_attempts=m.correct_attempts,
                    accuracy=round(accuracy, 4),
                    last_practiced=m.last_practiced,
                )
            )

        total_interactions = (
            db.query(Interaction)
            .filter(Interaction.user_id == current_user.id)
            .count()
        )
        correct_interactions = (
            db.query(Interaction)
            .filter(
                Interaction.user_id == current_user.id,
                Interaction.is_correct == True,  # noqa: E712
            )
            .count()
        )
        accuracy_rate = (
            correct_interactions / total_interactions if total_interactions > 0 else 0.0
        )

        recent_desc = (
            db.query(Interaction)
            .filter(Interaction.user_id == current_user.id)
            .order_by(Interaction.created_at.desc())
            .limit(50)
            .all()
        )

        current_streak = 0
        for inter in recent_desc:
            if inter.is_correct:
                current_streak += 1
            else:
                break

        chronological = list(reversed(recent_desc[:30]))
        elo_history: list[EloHistoryPoint] = [
            EloHistoryPoint(
                index=0,
                elo=1500.0 if not chronological else round(chronological[0].elo_before, 1),
                change=0.0,
                delta=0.0,
                is_correct=True,
                timestamp="Khởi điểm",
            )
        ]
        for idx, inter in enumerate(chronological, start=1):
            diff_val = round(inter.elo_after - inter.elo_before, 1)
            elo_history.append(
                EloHistoryPoint(
                    index=idx,
                    elo=round(inter.elo_after, 1),
                    change=diff_val,
                    delta=diff_val,
                    is_correct=bool(inter.is_correct),
                    timestamp=inter.created_at.strftime("%d/%m %H:%M") if inter.created_at else f"#{idx}",
                )
            )

        bloom_map = zpd_service.compute_user_bloom_mastery(db, current_user.id)
        unlocked_set = set(zpd_service.get_unlocked_bloom_levels(bloom_map))

        bloom_attempts: dict[int, tuple[int, int]] = {lvl: (0, 0) for lvl in range(1, 7)}
        inter_with_q = (
            db.query(Interaction.is_correct, Question.bloom_level)
            .join(Question, Question.id == Interaction.question_id)
            .filter(Interaction.user_id == current_user.id)
            .all()
        )
        for is_corr, b_lvl in inter_with_q:
            lvl = max(1, min(6, int(b_lvl or 1)))
            tot, corr = bloom_attempts[lvl]
            bloom_attempts[lvl] = (tot + 1, corr + (1 if is_corr else 0))

        bloom_radar: list[BloomRadarPoint] = []
        for lvl in range(1, 7):
            tot, corr = bloom_attempts[lvl]
            topic_mastery_val = bloom_map.get(lvl, 0.0)
            q_mastery_val = (corr / tot) if tot > 0 else 0.0
            combined_pct = round(max(topic_mastery_val, q_mastery_val) * 100.0, 1)
            bloom_radar.append(
                BloomRadarPoint(
                    bloom_level=lvl,
                    level=lvl,
                    label=BLOOM_LABELS[lvl],
                    mastery_percent=combined_pct,
                    mastery=combined_pct,
                    unlocked=(lvl in unlocked_set),
                    questions_attempted=tot,
                    attempts=tot,
                )
            )

        due_reviews_count = (
            db.query(SpacedRepetition)
            .filter(
                SpacedRepetition.user_id == current_user.id,
                SpacedRepetition.next_review <= datetime.now(timezone.utc),
            )
            .count()
        )

        return ProgressResponse(
            overall_elo=round(current_user.overall_elo, 2),
            topics_mastery=topics_mastery,
            total_questions_answered=total_interactions,
            accuracy_rate=round(accuracy_rate, 4),
            current_streak=current_streak,
            due_reviews_count=due_reviews_count,
            elo_history=elo_history,
            bloom_radar=bloom_radar,
        )


analytics_service = AnalyticsService()


def build_progress_response(db: Session, current_user: User) -> ProgressResponse:
    return analytics_service.build_user_progress(db, current_user)


def get_learner_mastery_details(
    db: Session,
    current_user: User,
) -> list[LearnerMasteryResponse]:
    masteries = (
        db.query(LearnerMastery)
        .filter(LearnerMastery.user_id == current_user.id)
        .all()
    )
    result: list[LearnerMasteryResponse] = []
    for m in masteries:
        topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
        if not topic:
            continue
        subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
        result.append(
            LearnerMasteryResponse(
                topic_id=m.topic_id,
                topic_name=topic.name,
                subject_name=subject.name if subject else "",
                mastery_score=round(m.mastery_score, 4),
                elo_rating=round(m.elo_rating, 2),
                total_attempts=m.total_attempts,
                correct_attempts=m.correct_attempts,
                bloom_level=topic.bloom_level,
                last_practiced=m.last_practiced,
            )
        )
    return result
