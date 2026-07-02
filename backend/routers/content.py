"""
Content Router - Quản lý và truy vấn nội dung học tập (Môn học, Chủ đề, Câu hỏi).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.content import Subject, Topic, Question
from models.user import User
from schemas.content import (
    SubjectResponse,
    TopicResponse,
    QuestionResponse,
    QuestionPublic,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["Content"])


@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả môn học.
    
    Trả về kèm số lượng chủ đề trong mỗi môn.
    """
    subjects = db.query(Subject).all()
    result = []
    
    for subject in subjects:
        topic_count = db.query(Topic).filter(Topic.subject_id == subject.id).count()
        result.append(SubjectResponse(
            id=subject.id,
            name=subject.name,
            description=subject.description,
            icon_emoji=subject.icon_emoji,
            topic_count=topic_count,
        ))
    
    return result


@router.get("/subjects/{subject_id}/topics", response_model=list[TopicResponse])
def list_topics(subject_id: int, db: Session = Depends(get_db)):
    """
    Lấy danh sách chủ đề trong một môn học.
    
    Sắp xếp theo order_index tăng dần.
    Trả về kèm số lượng câu hỏi trong mỗi chủ đề.
    """
    # Kiểm tra môn học tồn tại
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
    
    result = []
    for topic in topics:
        question_count = db.query(Question).filter(Question.topic_id == topic.id).count()
        result.append(TopicResponse(
            id=topic.id,
            subject_id=topic.subject_id,
            name=topic.name,
            description=topic.description,
            bloom_level=topic.bloom_level,
            order_index=topic.order_index,
            prerequisites=topic.prerequisites or [],
            question_count=question_count,
        ))
    
    return result


@router.get("/topics/{topic_id}/questions", response_model=list[QuestionPublic])
def list_questions(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách câu hỏi trong một chủ đề (KHÔNG bao gồm đáp án đúng).
    
    Yêu cầu xác thực để tránh người dùng không đăng nhập xem câu hỏi.
    Sắp xếp theo độ khó Elo tăng dần.
    """
    # Kiểm tra chủ đề tồn tại
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
