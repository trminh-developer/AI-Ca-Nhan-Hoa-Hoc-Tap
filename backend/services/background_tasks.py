from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import SessionLocal
from models.content import Question, Topic
from models.interaction import Interaction, LearnerMastery, SpacedRepetition
from models.user import User
from schemas.learning import QuizSubmit
from services.elo_engine import elo_engine
from services.sm2_engine import sm2_engine

def process_quiz_submission_bg(user_id: int, answers_data: list):
    """
    Background Task: Xử lý chấm điểm Elo và cập nhật SM-2 bất đồng bộ
    Nhận dictionary data từ router để không bị phụ thuộc vào phiên bản Pydantic
    """
    db: Session = SessionLocal()
    try:
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return

        for answer_item in answers_data:
            question_id = answer_item.get("question_id")
            selected_answer = answer_item.get("selected_answer", "")
            time_spent_ms = answer_item.get("time_spent_ms", 0)

            question = db.query(Question).filter(Question.id == question_id).first()
            if not question:
                continue
            
            is_correct = selected_answer.lower() == question.correct_answer.lower()
            actual_score = 1.0 if is_correct else 0.0
            
            # Cập nhật Elo
            elo_before = current_user.overall_elo
            new_learner_elo, new_item_elo = elo_engine.update_ratings(
                learner_rating=current_user.overall_elo,
                item_difficulty=question.difficulty_elo,
                actual_score=actual_score,
            )
            
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
                time_spent_ms=time_spent_ms,
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
                time_spent_ms=time_spent_ms,
                hints_used=0,
                elo_before=elo_before,
                elo_after=new_learner_elo,
            )
            db.add(interaction)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error in background task: {e}")
    finally:
        db.close()
