"""
Topics Endpoints - Danh sách câu hỏi theo chủ đề.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.content import Question, Topic
from app.models.user import User
from app.schemas.content import QuestionPublic

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/{topic_id}/questions", response_model=list[QuestionPublic])
def list_questions(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách câu hỏi trong một chủ đề (không bao gồm đáp án đúng),
    sắp xếp theo độ khó Elo tăng dần.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {topic_id}",
        )

    questions = (
        db.query(Question)
        .filter(Question.topic_id == topic_id)
        .order_by(Question.difficulty_elo)
        .all()
    )

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
