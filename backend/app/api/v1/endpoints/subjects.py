"""
Subjects Endpoints - Danh sách môn học và chủ đề theo môn học.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.content import Question, Subject, Topic
from app.schemas.content import SubjectResponse, TopicResponse

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả môn học kèm số lượng chủ đề."""
    subjects = db.query(Subject).all()
    result: list[SubjectResponse] = []

    for subject in subjects:
        topic_count = db.query(Topic).filter(Topic.subject_id == subject.id).count()
        result.append(
            SubjectResponse(
                id=subject.id,
                name=subject.name,
                description=subject.description,
                icon_emoji=subject.icon_emoji,
                topic_count=topic_count,
            )
        )
    return result


@router.get("/{subject_id}/topics", response_model=list[TopicResponse])
def list_topics(subject_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách chủ đề trong một môn học, sắp xếp theo order_index tăng dần."""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy môn học với ID {subject_id}",
        )

    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order_index)
        .all()
    )

    result: list[TopicResponse] = []
    for topic in topics:
        question_count = db.query(Question).filter(Question.topic_id == topic.id).count()
        raw_prereqs = topic.prerequisites
        if isinstance(raw_prereqs, str):
            try:
                parsed_prereqs = json.loads(raw_prereqs) if raw_prereqs.strip() else []
            except json.JSONDecodeError:
                parsed_prereqs = []
        else:
            parsed_prereqs = raw_prereqs or []

        result.append(
            TopicResponse(
                id=topic.id,
                subject_id=topic.subject_id,
                name=topic.name,
                description=topic.description,
                bloom_level=topic.bloom_level,
                order_index=topic.order_index,
                prerequisites=parsed_prereqs,
                question_count=question_count,
            )
        )
    return result
