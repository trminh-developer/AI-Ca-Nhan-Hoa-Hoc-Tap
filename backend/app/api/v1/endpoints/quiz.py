"""
Quiz & Adaptive Learning Endpoints - Trả lời câu hỏi thích ứng, ZPD Recommendation, Tiến độ & Mastery.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.content import Question, Topic
from app.models.interaction import Interaction, LearnerMastery, SpacedRepetition
from app.models.user import User
from app.schemas.learning import (
    AnswerResult,
    AnswerSubmit,
    LearnerMasteryResponse,
    NextQuestionResponse,
    ProgressResponse,
    QuizQuestion,
    QuizResult,
    QuizResultItem,
    QuizStart,
    QuizSubmit,
)
from app.services.analytics_service import (
    build_progress_response,
    get_learner_mastery_details,
)
from app.services.elo_service import elo_engine
from app.services.sm2_service import sm2_engine
from app.services.zpd_service import get_next_question, get_recommendation_reason

router = APIRouter(tags=["Adaptive Learning & Quiz"])


def _process_answer_submission(
    answer: AnswerSubmit,
    db: Session,
    current_user: User,
) -> AnswerResult:
    """
    Thực thi trọn vẹn chu trình thích ứng khép kín (Closed-Loop Adaptive Engine):
    1. Kiểm tra câu hỏi & đáp án
    2. Cập nhật Dual Elo (học viên & câu hỏi) với K-factor động theo số lần tương tác
    3. Cập nhật Learner Mastery cho chủ đề
    4. Cập nhật lịch trình ôn tập ngắt quãng SM-2
    5. Lưu nhật ký Interaction
    """
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy câu hỏi với ID {answer.question_id}",
        )

    is_correct = answer.selected_answer.strip().lower() == question.correct_answer.strip().lower()
    actual_score = 1.0 if is_correct else 0.0

    # Đếm số tương tác của học viên để co giãn K-factor động
    learner_attempts = (
        db.query(Interaction).filter(Interaction.user_id == current_user.id).count()
    )

    elo_before = current_user.overall_elo
    new_learner_elo, new_item_elo = elo_engine.update_ratings(
        learner_rating=current_user.overall_elo,
        item_difficulty=question.difficulty_elo,
        actual_score=actual_score,
        learner_attempts=learner_attempts,
    )
    elo_change = new_learner_elo - elo_before

    current_user.overall_elo = new_learner_elo
    question.difficulty_elo = new_item_elo

    # Cập nhật Learner Mastery cho chủ đề
    mastery = (
        db.query(LearnerMastery)
        .filter(
            LearnerMastery.user_id == current_user.id,
            LearnerMastery.topic_id == question.topic_id,
        )
        .first()
    )
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
        learner_attempts=mastery.total_attempts,
    )
    mastery.elo_rating = topic_new_elo
    mastery.last_practiced = datetime.now(timezone.utc)

    # Cập nhật SM-2 Spaced Repetition
    sr = (
        db.query(SpacedRepetition)
        .filter(
            SpacedRepetition.user_id == current_user.id,
            SpacedRepetition.question_id == question.id,
        )
        .first()
    )

    expected_success = elo_engine.expected_score(elo_before, question.difficulty_elo)
    quality = sm2_engine.calculate_quality(
        is_correct=is_correct,
        time_spent_ms=answer.time_spent_ms,
        hints_used=answer.hints_used,
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

    # Lưu Interaction log
    interaction = Interaction(
        user_id=current_user.id,
        question_id=question.id,
        is_correct=is_correct,
        time_spent_ms=answer.time_spent_ms,
        hints_used=answer.hints_used,
        elo_before=elo_before,
        elo_after=new_learner_elo,
    )
    db.add(interaction)
    db.commit()

    xp_earned = elo_engine.calculate_xp(elo_change, is_correct)

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        elo_change=round(elo_change, 2),
        new_elo=round(new_learner_elo, 2),
        xp_earned=xp_earned,
        sm2_quality=quality,
        next_review_days=new_interval,
        easiness_factor=new_ef,
    )


def _fetch_next_zpd_question(
    db: Session,
    current_user: User,
    topic_id: Optional[int] = None,
) -> NextQuestionResponse:
    """Lấy câu hỏi ZPD tiếp theo cho học viên."""
    question = get_next_question(db, current_user.id, topic_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không còn câu hỏi phù hợp. Hãy thử chủ đề khác!",
        )

    if topic_id:
        mastery = (
            db.query(LearnerMastery)
            .filter(
                LearnerMastery.user_id == current_user.id,
                LearnerMastery.topic_id == topic_id,
            )
            .first()
        )
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


@router.post("/learning/answer", response_model=AnswerResult)
def submit_learning_answer(
    answer: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gửi câu trả lời học tập thích ứng và cập nhật Dual Elo + SM-2."""
    return _process_answer_submission(answer, db, current_user)


@router.get("/learning/next-question", response_model=NextQuestionResponse)
def get_next_learning_question(
    topic_id: Optional[int] = Query(None, description="ID chủ đề (tùy chọn)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy câu hỏi tiếp theo được đề xuất trong vùng phát triển gần nhất (ZPD)."""
    return _fetch_next_zpd_question(db, current_user, topic_id)


@router.post("/quiz/start", response_model=list[QuizQuestion])
def start_quiz_session(
    quiz_data: QuizStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bắt đầu bài kiểm tra thích ứng - Chọn N câu hỏi phù hợp trong vùng ZPD của học viên.
    """
    topic = db.query(Topic).filter(Topic.id == quiz_data.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chủ đề với ID {quiz_data.topic_id}",
        )

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

    mastery = (
        db.query(LearnerMastery)
        .filter(
            LearnerMastery.user_id == current_user.id,
            LearnerMastery.topic_id == quiz_data.topic_id,
        )
        .first()
    )
    learner_elo = mastery.elo_rating if mastery else current_user.overall_elo
    num_requested = min(quiz_data.num_questions, len(all_questions))

    selected = elo_engine.select_optimal_content(
        learner_elo=learner_elo,
        available_items=all_questions,
        max_items=num_requested,
    )

    if len(selected) < num_requested:
        selected_ids = {q.id for q in selected}
        remaining = [q for q in all_questions if q.id not in selected_ids]
        remaining.sort(
            key=lambda q: abs(
                elo_engine.expected_score(learner_elo, q.difficulty_elo) - 0.675
            )
        )
        needed = num_requested - len(selected)
        selected.extend(remaining[:needed])

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


@router.post("/quiz/submit", response_model=QuizResult)
def submit_quiz_batch(
    quiz: QuizSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Nộp danh sách câu trả lời trong bài kiểm tra và cập nhật Elo + SM-2."""
    if not quiz.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bài kiểm tra không có câu trả lời nào",
        )

    results: list[QuizResultItem] = []
    total_elo_change = 0.0
    correct_count = 0

    for item in quiz.answers:
        question = db.query(Question).filter(Question.id == item.question_id).first()
        if not question:
            continue
        ans_result = _process_answer_submission(
            AnswerSubmit(
                question_id=item.question_id,
                selected_answer=item.selected_answer,
                time_spent_ms=item.time_spent_ms,
            ),
            db=db,
            current_user=current_user,
        )
        if ans_result.is_correct:
            correct_count += 1
        total_elo_change += ans_result.elo_change
        results.append(
            QuizResultItem(
                question_id=question.id,
                is_correct=ans_result.is_correct,
                correct_answer=ans_result.correct_answer,
                explanation=ans_result.explanation,
                elo_change=ans_result.elo_change,
            )
        )

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


@router.get("/learning/progress", response_model=ProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy tổng quan tiến độ học tập, chuỗi Elo biến thiên theo thời gian,
    biểu đồ Radar 6 cấp độ Bloom, và số câu hỏi đến hạn ôn tập SM-2.
    """
    return build_progress_response(db, current_user)


@router.get("/learning/mastery", response_model=list[LearnerMasteryResponse])
def get_mastery(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy mức độ thành thạo chi tiết theo từng chủ đề."""
    return get_learner_mastery_details(db, current_user)
