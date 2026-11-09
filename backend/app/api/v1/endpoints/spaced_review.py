"""
Spaced Repetition (SM-2) Endpoints - Hàng đợi ôn tập trí nhớ dài hạn Ebbinghaus.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.content import Question, Topic
from app.models.interaction import SpacedRepetition
from app.models.user import User
from app.schemas.content import QuestionPublic
from app.schemas.learning import (
    AnswerResult,
    AnswerSubmit,
    SpacedReviewCard,
)
from app.services.zpd_service import get_review_questions
from app.api.v1.endpoints.quiz import _process_answer_submission

router = APIRouter(tags=["Spaced Repetition (SM-2)"])


@router.get("/learning/review-queue", response_model=list[QuestionPublic])
def get_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách câu hỏi đến hạn ôn tập SM-2 (`next_review <= now`).
    """
    questions = get_review_questions(db, current_user.id)
    return [
        QuestionPublic(
            id=q.id,
            topic_id=q.topic_id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty_elo=q.difficulty_elo,
            bloom_level=q.bloom_level,
        )
        for q in questions
    ]


@router.get("/spaced-review/due", response_model=list[SpacedReviewCard])
def get_due_spaced_review_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách thẻ Flashcard SM-2 đến hạn ôn tập kèm thông số EF, Interval, Repetitions.
    """
    now = datetime.now(timezone.utc)
    records = (
        db.query(SpacedRepetition)
        .filter(
            SpacedRepetition.user_id == current_user.id,
            SpacedRepetition.next_review <= now,
        )
        .order_by(SpacedRepetition.next_review.asc())
        .limit(20)
        .all()
    )

    cards: list[SpacedReviewCard] = []
    for sr in records:
        q = db.query(Question).filter(Question.id == sr.question_id).first()
        if not q:
            continue
        topic = db.query(Topic).filter(Topic.id == q.topic_id).first()
        cards.append(
            SpacedReviewCard(
                id=q.id,
                topic_id=q.topic_id,
                topic_name=topic.name if topic else "",
                question_text=q.question_text,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                difficulty_elo=q.difficulty_elo,
                bloom_level=q.bloom_level,
                repetitions=sr.repetitions,
                interval_days=sr.interval_days,
                easiness_factor=round(sr.easiness_factor, 2),
                next_review=sr.next_review,
            )
        )
    return cards


@router.post("/spaced-review/answer", response_model=AnswerResult)
def submit_spaced_review_answer(
    answer: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gửi kết quả ôn tập thẻ SM-2 và tính toán lại khoảng cách lặp lại tiếp theo.
    """
    return _process_answer_submission(answer, db, current_user)
