"""
Assessment Router - Quản lý bài kiểm tra (quiz) theo Elo.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.content import Question, Topic
from models.interaction import Interaction, LearnerMastery, SpacedRepetition
from models.user import User
from schemas.learning import (
    QuizStart,
    QuizQuestion,
    QuizSubmit,
    QuizResult,
    QuizResultItem,
)
from services.auth_service import get_current_user
from services.elo_engine import elo_engine
from services.sm2_engine import sm2_engine

router = APIRouter(prefix="/api/quiz", tags=["Quiz / Assessment"])


@router.post("/start", response_model=list[QuizQuestion])
def start_quiz(
    quiz_data: QuizStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bắt đầu bài kiểm tra - Chọn N câu hỏi phù hợp theo Elo.
    
    Quy trình:
    1. Kiểm tra topic tồn tại và có đủ câu hỏi
    2. Dùng Elo Engine chọn câu hỏi trong ZPD
    3. Bổ sung thêm câu nếu ZPD không đủ
    4. Trả về danh sách câu hỏi (không có đáp án)
    """
    # Kiểm tra topic tồn tại
    topic = db.query(Topic).filter(Topic.id == quiz_data.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {quiz_data.topic_id}",
        )
    
    # Lấy tất cả câu hỏi của topic
    all_questions = (
        db.query(Question)
        .filter(Question.topic_id == quiz_data.topic_id)
        .all()
    )
    
    if not all_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chủ đề '{topic.name}' chưa có câu hỏi nào",
        )
    
    # Lấy Elo của học sinh cho topic
    mastery = db.query(LearnerMastery).filter(
        LearnerMastery.user_id == current_user.id,
        LearnerMastery.topic_id == quiz_data.topic_id,
    ).first()
    
    learner_elo = mastery.elo_rating if mastery else current_user.overall_elo
    
    # Chọn câu hỏi bằng Elo Engine (ZPD selection)
    num_requested = min(quiz_data.num_questions, len(all_questions))
    
    selected = elo_engine.select_optimal_content(
        learner_elo=learner_elo,
        available_items=all_questions,
        max_items=num_requested,
    )
    
    # Nếu ZPD không đủ câu hỏi, bổ sung thêm
    if len(selected) < num_requested:
        selected_ids = {q.id for q in selected}
        remaining = [q for q in all_questions if q.id not in selected_ids]
        
        # Sắp xếp remaining theo khoảng cách Elo gần nhất
        remaining.sort(
            key=lambda q: abs(
                elo_engine.expected_score(learner_elo, q.difficulty_elo) - 0.75
            )
        )
        
        needed = num_requested - len(selected)
        selected.extend(remaining[:needed])
    
    # Trả về danh sách câu hỏi (không có đáp án)
    return [
        QuizQuestion(
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
        for q in selected
    ]


@router.post("/submit", response_model=QuizResult)
def submit_quiz(
    quiz: QuizSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Nộp bài kiểm tra - Xử lý tất cả câu trả lời và trả về kết quả.
    
    Quy trình cho mỗi câu:
    1. Kiểm tra đáp án
    2. Cập nhật Elo (user + question)
    3. Cập nhật Learner Mastery
    4. Cập nhật SM-2
    5. Lưu Interaction
    
    Cuối cùng trả về tổng kết: số đúng, tỉ lệ, thay đổi Elo.
    """
    if not quiz.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bài kiểm tra không có câu trả lời nào",
        )
    
    results = []
    total_elo_change = 0.0
    correct_count = 0
    
    for answer_item in quiz.answers:
        # Lấy câu hỏi
        question = db.query(Question).filter(Question.id == answer_item.question_id).first()
        if not question:
            continue  # Bỏ qua câu hỏi không tồn tại
        
        # Kiểm tra đáp án
        is_correct = answer_item.selected_answer.lower() == question.correct_answer.lower()
        actual_score = 1.0 if is_correct else 0.0
        
        if is_correct:
            correct_count += 1
        
        # Cập nhật Elo
        elo_before = current_user.overall_elo
        new_learner_elo, new_item_elo = elo_engine.update_ratings(
            learner_rating=current_user.overall_elo,
            item_difficulty=question.difficulty_elo,
            actual_score=actual_score,
        )
        
        elo_change = new_learner_elo - elo_before
        total_elo_change += elo_change
        
        current_user.overall_elo = new_learner_elo
        question.difficulty_elo = new_item_elo
        
        # Cập nhật Learner Mastery
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
        mastery.mastery_score = mastery.correct_attempts / mastery.total_attempts
        
        topic_new_elo, _ = elo_engine.update_ratings(
            learner_rating=mastery.elo_rating,
            item_difficulty=question.difficulty_elo,
            actual_score=actual_score,
        )
        mastery.elo_rating = topic_new_elo
        mastery.last_practiced = datetime.now(timezone.utc)
        
        # Cập nhật SM-2
        sr = db.query(SpacedRepetition).filter(
            SpacedRepetition.user_id == current_user.id,
            SpacedRepetition.question_id == question.id,
        ).first()
        
        expected_success = elo_engine.expected_score(
            current_user.overall_elo, question.difficulty_elo
        )
        quality = sm2_engine.calculate_quality(
            is_correct=is_correct,
            time_spent_ms=answer_item.time_spent_ms,
            expected_success=expected_success,
        )
        
        if not sr:
            sr = SpacedRepetition(
                user_id=current_user.id,
                question_id=question.id,
            )
            db.add(sr)
            db.flush()
        
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
        
        # Lưu Interaction
        interaction = Interaction(
            user_id=current_user.id,
            question_id=question.id,
            is_correct=is_correct,
            time_spent_ms=answer_item.time_spent_ms,
            hints_used=0,
            elo_before=elo_before,
            elo_after=new_learner_elo,
        )
        db.add(interaction)
        
        results.append(QuizResultItem(
            question_id=question.id,
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            elo_change=round(elo_change, 2),
        ))
    
    # Commit tất cả
    db.commit()
    
    total_questions = len(results)
    accuracy = correct_count / total_questions if total_questions > 0 else 0.0
    
    return QuizResult(
        total_questions=total_questions,
        correct_count=correct_count,
        accuracy=round(accuracy, 4),
        total_elo_change=round(total_elo_change, 2),
        new_elo=round(current_user.overall_elo, 2),
        results=results,
    )
