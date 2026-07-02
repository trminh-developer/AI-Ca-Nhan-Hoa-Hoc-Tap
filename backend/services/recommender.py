"""
Content Recommender - Đề xuất nội dung học tập thích ứng.

Kết hợp Elo Rating và SM-2 để:
1. Chọn câu hỏi tiếp theo trong ZPD (Vùng Phát triển Gần nhất)
2. Ưu tiên câu hỏi cần ôn tập (SM-2)
3. Đề xuất chủ đề phù hợp với trình độ
"""

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.content import Question, Topic, Subject
from models.interaction import LearnerMastery, SpacedRepetition, Interaction
from models.user import User
from services.elo_engine import elo_engine


def get_next_question(
    db: Session,
    user_id: int,
    topic_id: Optional[int] = None,
) -> Optional[Question]:
    """
    Lấy câu hỏi tiếp theo phù hợp nhất cho học sinh.
    
    Chiến lược:
    1. Ưu tiên câu hỏi cần ôn tập (SM-2 review queue)
    2. Nếu không có, chọn câu hỏi mới trong ZPD
    3. Tránh câu hỏi vừa trả lời gần đây
    
    Args:
        db: Database session
        user_id: ID người dùng
        topic_id: ID chủ đề (tùy chọn, nếu None thì chọn từ mọi chủ đề)
        
    Returns:
        Question phù hợp nhất hoặc None nếu không còn câu hỏi
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Lấy Elo của học sinh cho topic cụ thể (hoặc tổng thể)
    if topic_id:
        mastery = db.query(LearnerMastery).filter(
            LearnerMastery.user_id == user_id,
            LearnerMastery.topic_id == topic_id,
        ).first()
        learner_elo = mastery.elo_rating if mastery else user.overall_elo
    else:
        learner_elo = user.overall_elo
    
    # Bước 1: Kiểm tra câu hỏi cần ôn tập
    review_question = _get_review_question(db, user_id, topic_id)
    if review_question:
        return review_question
    
    # Bước 2: Lấy danh sách câu hỏi chưa trả lời hoặc đã lâu chưa ôn
    answered_recently = (
        db.query(Interaction.question_id)
        .filter(Interaction.user_id == user_id)
        .order_by(Interaction.created_at.desc())
        .limit(20)  # Tránh 20 câu gần đây nhất
        .subquery()
    )
    
    query = db.query(Question).filter(
        Question.id.notin_(answered_recently)
    )
    
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    
    available_questions = query.all()
    
    # Nếu đã trả lời hết, cho phép lặp lại (loại bỏ filter)
    if not available_questions:
        query = db.query(Question)
        if topic_id:
            query = query.filter(Question.topic_id == topic_id)
        available_questions = query.all()
    
    if not available_questions:
        return None
    
    # Bước 3: Dùng Elo Engine để chọn câu hỏi trong ZPD
    optimal_questions = elo_engine.select_optimal_content(
        learner_elo=learner_elo,
        available_items=available_questions,
        max_items=5,
    )
    
    return optimal_questions[0] if optimal_questions else available_questions[0]


def _get_review_question(
    db: Session,
    user_id: int,
    topic_id: Optional[int] = None,
) -> Optional[Question]:
    """Lấy câu hỏi đến hạn ôn tập (SM-2) sớm nhất."""
    query = (
        db.query(SpacedRepetition)
        .filter(
            SpacedRepetition.user_id == user_id,
            SpacedRepetition.next_review <= date.today(),
        )
        .order_by(SpacedRepetition.next_review.asc())
    )
    
    if topic_id:
        # Lọc theo topic thông qua Question
        question_ids = (
            db.query(Question.id)
            .filter(Question.topic_id == topic_id)
            .subquery()
        )
        query = query.filter(SpacedRepetition.question_id.in_(question_ids))
    
    sr = query.first()
    if sr:
        return db.query(Question).filter(Question.id == sr.question_id).first()
    return None


def get_review_questions(
    db: Session,
    user_id: int,
    limit: int = 20,
) -> list[Question]:
    """
    Lấy danh sách câu hỏi cần ôn tập theo SM-2.
    
    Args:
        db: Database session
        user_id: ID người dùng
        limit: Số lượng câu hỏi tối đa
        
    Returns:
        Danh sách câu hỏi cần ôn tập, sắp xếp theo ngày review (sớm nhất trước)
    """
    sr_list = (
        db.query(SpacedRepetition)
        .filter(
            SpacedRepetition.user_id == user_id,
            SpacedRepetition.next_review <= date.today(),
        )
        .order_by(SpacedRepetition.next_review.asc())
        .limit(limit)
        .all()
    )
    
    question_ids = [sr.question_id for sr in sr_list]
    if not question_ids:
        return []
    
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    
    # Sắp xếp lại theo thứ tự ưu tiên ôn tập
    id_order = {qid: i for i, qid in enumerate(question_ids)}
    questions.sort(key=lambda q: id_order.get(q.id, 999))
    
    return questions


def get_recommended_topics(
    db: Session,
    user_id: int,
) -> list[dict]:
    """
    Đề xuất chủ đề học tập ưu tiên cho học sinh.
    
    Tiêu chí ưu tiên (từ cao đến thấp):
    1. Chủ đề chưa bắt đầu nhưng đã đủ điều kiện tiên quyết
    2. Chủ đề có mastery thấp (< 0.5)
    3. Chủ đề đã lâu chưa luyện tập
    4. Chủ đề theo thứ tự Bloom's level tăng dần
    
    Args:
        db: Database session
        user_id: ID người dùng
        
    Returns:
        Danh sách chủ đề với thông tin ưu tiên, sắp xếp theo mức ưu tiên giảm dần
    """
    # Lấy tất cả chủ đề
    all_topics = db.query(Topic).order_by(Topic.order_index).all()
    
    # Lấy mastery hiện tại của user
    masteries = (
        db.query(LearnerMastery)
        .filter(LearnerMastery.user_id == user_id)
        .all()
    )
    mastery_map = {m.topic_id: m for m in masteries}
    
    # Xác định chủ đề đã thành thạo (để kiểm tra điều kiện tiên quyết)
    mastered_topic_ids = {
        m.topic_id for m in masteries if m.mastery_score >= 0.6
    }
    
    recommended = []
    
    for topic in all_topics:
        mastery = mastery_map.get(topic.id)
        prerequisites = topic.prerequisites or []
        
        # Kiểm tra điều kiện tiên quyết
        prereqs_met = all(p_id in mastered_topic_ids for p_id in prerequisites)
        
        if not prereqs_met:
            continue  # Bỏ qua chủ đề chưa đủ điều kiện
        
        # Tính điểm ưu tiên
        priority_score = 0.0
        reason = ""
        
        if mastery is None:
            # Chủ đề chưa bắt đầu -> ưu tiên cao
            priority_score = 100.0 - topic.bloom_level * 10
            reason = "Chủ đề mới - sẵn sàng bắt đầu học"
        elif mastery.mastery_score < 0.3:
            # Mastery rất thấp -> cần ôn tập gấp
            priority_score = 90.0 - mastery.mastery_score * 100
            reason = f"Cần cải thiện - mastery chỉ {mastery.mastery_score:.0%}"
        elif mastery.mastery_score < 0.6:
            # Mastery trung bình -> nên ôn thêm
            priority_score = 60.0 - mastery.mastery_score * 50
            reason = f"Chưa thành thạo - mastery {mastery.mastery_score:.0%}"
        elif mastery.mastery_score < 0.85:
            # Mastery khá -> cần luyện thêm
            priority_score = 30.0
            reason = f"Gần thành thạo - mastery {mastery.mastery_score:.0%}"
        else:
            # Đã thành thạo -> ưu tiên thấp
            priority_score = 10.0
            reason = f"Đã thành thạo - mastery {mastery.mastery_score:.0%}"
        
        # Lấy tên subject
        subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()
        
        recommended.append({
            "topic_id": topic.id,
            "topic_name": topic.name,
            "subject_name": subject.name if subject else "",
            "bloom_level": topic.bloom_level,
            "mastery_score": mastery.mastery_score if mastery else 0.0,
            "elo_rating": mastery.elo_rating if mastery else 1500.0,
            "priority_score": priority_score,
            "reason": reason,
        })
    
    # Sắp xếp theo ưu tiên giảm dần
    recommended.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return recommended


def get_recommendation_reason(
    learner_elo: float,
    question: Question,
) -> str:
    """
    Tạo lý do đề xuất câu hỏi cho học sinh.
    
    Args:
        learner_elo: Elo hiện tại của học sinh
        question: Câu hỏi được đề xuất
        
    Returns:
        Chuỗi giải thích lý do đề xuất
    """
    success_prob = elo_engine.expected_score(learner_elo, question.difficulty_elo)
    difficulty_label = elo_engine.get_difficulty_label(question.difficulty_elo)
    
    if success_prob >= 0.85:
        return f"Câu hỏi ôn tập ({difficulty_label}) - Xác suất đúng: {success_prob:.0%}. Củng cố kiến thức đã học."
    elif success_prob >= 0.70:
        return f"Câu hỏi trong vùng phát triển ({difficulty_label}) - Xác suất đúng: {success_prob:.0%}. Thử thách vừa phải, tối ưu cho học tập."
    elif success_prob >= 0.50:
        return f"Câu hỏi thử thách ({difficulty_label}) - Xác suất đúng: {success_prob:.0%}. Nâng cao kỹ năng."
    else:
        return f"Câu hỏi nâng cao ({difficulty_label}) - Xác suất đúng: {success_prob:.0%}. Mở rộng giới hạn kiến thức."
