"""
Learning Router - Xử lý tương tác học tập: trả lời câu hỏi, tiến độ, mastery, ôn tập.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.content import Question, Topic, Subject
from models.interaction import Interaction, LearnerMastery, SpacedRepetition
from models.user import User
from schemas.learning import (
    AnswerSubmit,
    AnswerResult,
    NextQuestionResponse,
    ProgressResponse,
    TopicMasteryItem,
    LearnerMasteryResponse,
)
from schemas.content import QuestionPublic
from services.auth_service import get_current_user
from services.elo_engine import elo_engine
from services.sm2_engine import sm2_engine
from services.recommender import (
    get_next_question,
    get_review_questions,
    get_recommendation_reason,
)

router = APIRouter(prefix="/api/learning", tags=["Learning"])


@router.post("/answer", response_model=AnswerResult)
def submit_answer(
    answer: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gửi câu trả lời và nhận kết quả.
    
    Quy trình:
    1. Kiểm tra câu hỏi tồn tại
    2. So sánh đáp án
    3. Cập nhật Elo (học sinh + câu hỏi)
    4. Cập nhật Learner Mastery
    5. Cập nhật SM-2 Spaced Repetition
    6. Lưu Interaction log
    """
    # 1. Lấy câu hỏi
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu hỏi với ID {answer.question_id}",
        )
    
    # 2. Kiểm tra đáp án
    is_correct = answer.selected_answer.lower() == question.correct_answer.lower()
    actual_score = 1.0 if is_correct else 0.0
    
    # 3. Cập nhật Elo
    elo_before = current_user.overall_elo
    new_learner_elo, new_item_elo = elo_engine.update_ratings(
        learner_rating=current_user.overall_elo,
        item_difficulty=question.difficulty_elo,
        actual_score=actual_score,
    )
    
    elo_change = new_learner_elo - elo_before
    
    # Cập nhật Elo cho user
    current_user.overall_elo = new_learner_elo
    
    # Cập nhật Elo cho câu hỏi
    question.difficulty_elo = new_item_elo
    
    # 4. Cập nhật Learner Mastery cho topic
    mastery = db.query(LearnerMastery).filter(
        LearnerMastery.user_id == current_user.id,
        LearnerMastery.topic_id == question.topic_id,
    ).first()
    
    if not mastery:
        mastery = LearnerMastery(
            user_id=current_user.id,
            topic_id=question.topic_id,
            mastery_score=0.0,
            elo_rating=1500.0,
            total_attempts=0,
            correct_attempts=0,
        )
        db.add(mastery)
    
    mastery.total_attempts += 1
    if is_correct:
        mastery.correct_attempts += 1
    
    # Cập nhật mastery score (tỉ lệ đúng có trọng số)
    mastery.mastery_score = mastery.correct_attempts / mastery.total_attempts
    
    # Cập nhật Elo cho topic
    topic_new_elo, _ = elo_engine.update_ratings(
        learner_rating=mastery.elo_rating,
        item_difficulty=question.difficulty_elo,
        actual_score=actual_score,
    )
    mastery.elo_rating = topic_new_elo
    mastery.last_practiced = datetime.now(timezone.utc)
    
    # 5. Cập nhật SM-2 Spaced Repetition
    sr = db.query(SpacedRepetition).filter(
        SpacedRepetition.user_id == current_user.id,
        SpacedRepetition.question_id == question.id,
    ).first()
    
    # Tính expected success cho SM-2 quality
    expected_success = elo_engine.expected_score(
        current_user.overall_elo, question.difficulty_elo
    )
    
    quality = sm2_engine.calculate_quality(
        is_correct=is_correct,
        time_spent_ms=answer.time_spent_ms,
        hints_used=0,  # Hints tracked separately
        expected_success=expected_success,
    )
    
    if not sr:
        sr = SpacedRepetition(
            user_id=current_user.id,
            question_id=question.id,
        )
        db.add(sr)
        db.flush()  # Để lấy default values
    
    new_interval, new_reps, new_ef = sm2_engine.update(
        quality=quality,
        repetitions=sr.repetitions,
        interval=sr.interval_days,
        easiness_factor=sr.easiness_factor,
    )
    
    sr.interval_days = new_interval
    sr.repetitions = new_reps
    sr.easiness_factor = new_ef
    sr.next_review = sm2_engine.get_next_review_date(new_interval)
    
    # 6. Lưu Interaction log
    interaction = Interaction(
        user_id=current_user.id,
        question_id=question.id,
        is_correct=is_correct,
        time_spent_ms=answer.time_spent_ms,
        hints_used=0,
        elo_before=elo_before,
        elo_after=new_learner_elo,
    )
    db.add(interaction)
    
    # Commit tất cả thay đổi
    db.commit()
    
    # Tính XP
    xp_earned = elo_engine.calculate_xp(elo_change, is_correct)
    
    return AnswerResult(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        elo_change=round(elo_change, 2),
        new_elo=round(new_learner_elo, 2),
        xp_earned=xp_earned,
    )


@router.get("/next-question", response_model=NextQuestionResponse)
def get_next(
    topic_id: Optional[int] = Query(None, description="ID chủ đề (tùy chọn)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy câu hỏi tiếp theo được đề xuất (dựa trên Elo + SM-2).
    
    Nếu topic_id được cung cấp, chỉ chọn từ topic đó.
    Nếu không, chọn từ tất cả các topic.
    """
    question = get_next_question(db, current_user.id, topic_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không còn câu hỏi phù hợp. Hãy thử chủ đề khác!",
        )
    
    # Lấy Elo phù hợp (topic-specific hoặc overall)
    if topic_id:
        mastery = db.query(LearnerMastery).filter(
            LearnerMastery.user_id == current_user.id,
            LearnerMastery.topic_id == topic_id,
        ).first()
        learner_elo = mastery.elo_rating if mastery else current_user.overall_elo
    else:
        learner_elo = current_user.overall_elo
    
    reason = get_recommendation_reason(learner_elo, question)
    
    return NextQuestionResponse(
        id=question.id,
        topic_id=question.topic_id,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        difficulty_elo=question.difficulty_elo,
        bloom_level=question.bloom_level,
        recommendation_reason=reason,
    )


@router.get("/progress", response_model=ProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy tổng quan tiến độ học tập của người dùng.
    
    Bao gồm: Elo tổng thể, mastery từng chủ đề, tổng số câu đã trả lời,
    tỉ lệ chính xác, và chuỗi đúng liên tiếp.
    """
    # Lấy tất cả mastery records
    masteries = (
        db.query(LearnerMastery)
        .filter(LearnerMastery.user_id == current_user.id)
        .all()
    )
    
    # Xây dựng danh sách mastery theo topic
    topics_mastery = []
    for m in masteries:
        topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
        if not topic:
            continue
        
        accuracy = m.correct_attempts / m.total_attempts if m.total_attempts > 0 else 0.0
        topics_mastery.append(TopicMasteryItem(
            topic_id=m.topic_id,
            topic_name=topic.name,
            mastery_score=round(m.mastery_score, 4),
            elo_rating=round(m.elo_rating, 2),
            total_attempts=m.total_attempts,
            correct_attempts=m.correct_attempts,
            accuracy=round(accuracy, 4),
            last_practiced=m.last_practiced,
        ))
    
    # Tổng số câu đã trả lời và tỉ lệ đúng
    total_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id)
        .count()
    )
    
    correct_interactions = (
        db.query(Interaction)
        .filter(
            Interaction.user_id == current_user.id,
            Interaction.is_correct == True,
        )
        .count()
    )
    
    accuracy_rate = correct_interactions / total_interactions if total_interactions > 0 else 0.0
    
    # Tính chuỗi đúng liên tiếp hiện tại
    recent_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id)
        .order_by(Interaction.created_at.desc())
        .limit(100)
        .all()
    )
    
    current_streak = 0
    for interaction in recent_interactions:
        if interaction.is_correct:
            current_streak += 1
        else:
            break
    
    return ProgressResponse(
        overall_elo=round(current_user.overall_elo, 2),
        topics_mastery=topics_mastery,
        total_questions_answered=total_interactions,
        accuracy_rate=round(accuracy_rate, 4),
        current_streak=current_streak,
    )


@router.get("/mastery", response_model=list[LearnerMasteryResponse])
def get_mastery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy mức độ thành thạo theo từng chủ đề.
    
    Trả về chi tiết mastery bao gồm thông tin topic và subject.
    """
    masteries = (
        db.query(LearnerMastery)
        .filter(LearnerMastery.user_id == current_user.id)
        .all()
    )
    
    result = []
    for m in masteries:
        topic = db.query(Topic).filter(Topic.id == m.topic_id).first()
        if not topic:
            continue
        
        subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
        
        result.append(LearnerMasteryResponse(
            topic_id=m.topic_id,
            topic_name=topic.name,
            subject_name=subject.name if subject else "",
            mastery_score=round(m.mastery_score, 4),
            elo_rating=round(m.elo_rating, 2),
            total_attempts=m.total_attempts,
            correct_attempts=m.correct_attempts,
            bloom_level=topic.bloom_level,
            last_practiced=m.last_practiced,
        ))
    
    return result


@router.get("/review-queue", response_model=list[QuestionPublic])
def get_review_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách câu hỏi cần ôn tập (SM-2 review queue).
    
    Trả về các câu hỏi có next_review <= ngày hôm nay.
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
