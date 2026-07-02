"""
Pydantic Schemas cho Học tập thích ứng - Submit/Result, Quiz, Progress, Mastery.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ======================== Answer Schemas ========================

class AnswerSubmit(BaseModel):
    """Schema gửi câu trả lời."""
    question_id: int = Field(..., description="ID câu hỏi")
    selected_answer: str = Field(..., pattern="^[abcd]$", description="Đáp án được chọn (a/b/c/d)")
    time_spent_ms: int = Field(0, ge=0, description="Thời gian trả lời (ms)")


class AnswerResult(BaseModel):
    """Schema kết quả sau khi trả lời."""
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    elo_change: float = Field(..., description="Thay đổi Elo (+/-)")
    new_elo: float = Field(..., description="Elo mới sau khi trả lời")
    xp_earned: int = Field(0, description="Điểm kinh nghiệm nhận được")


# ======================== Quiz Schemas ========================

class QuizStart(BaseModel):
    """Schema bắt đầu bài kiểm tra."""
    topic_id: int = Field(..., description="ID chủ đề")
    num_questions: int = Field(10, ge=1, le=50, description="Số câu hỏi")


class QuizQuestion(BaseModel):
    """Schema câu hỏi trong bài kiểm tra (không có đáp án đúng)."""
    id: int
    topic_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_elo: float
    bloom_level: int

    model_config = {"from_attributes": True}


class QuizSubmitItem(BaseModel):
    """Schema một câu trả lời trong bài quiz."""
    question_id: int
    selected_answer: str = Field(..., pattern="^[abcd]$")
    time_spent_ms: int = Field(0, ge=0)


class QuizSubmit(BaseModel):
    """Schema gửi toàn bộ bài kiểm tra."""
    answers: list[QuizSubmitItem]


class QuizResultItem(BaseModel):
    """Schema kết quả từng câu trong bài quiz."""
    question_id: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    elo_change: float


class QuizResult(BaseModel):
    """Schema kết quả tổng hợp bài kiểm tra."""
    total_questions: int
    correct_count: int
    accuracy: float = Field(..., description="Tỉ lệ đúng (0.0 - 1.0)")
    total_elo_change: float
    new_elo: float
    results: list[QuizResultItem]


# ======================== Progress Schemas ========================

class TopicMasteryItem(BaseModel):
    """Schema thông tin thành thạo cho một chủ đề."""
    topic_id: int
    topic_name: str
    mastery_score: float
    elo_rating: float
    total_attempts: int
    correct_attempts: int
    accuracy: float = Field(..., description="Tỉ lệ đúng cho chủ đề")
    last_practiced: Optional[datetime]


class ProgressResponse(BaseModel):
    """Schema tổng quan tiến độ học tập."""
    overall_elo: float
    topics_mastery: list[TopicMasteryItem]
    total_questions_answered: int
    accuracy_rate: float = Field(..., description="Tỉ lệ đúng tổng thể")
    current_streak: int = Field(0, description="Chuỗi trả lời đúng liên tiếp hiện tại")


# ======================== Recommendation Schemas ========================

class NextQuestionResponse(BaseModel):
    """Schema câu hỏi được đề xuất tiếp theo."""
    id: int
    topic_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_elo: float
    bloom_level: int
    recommendation_reason: str = Field(..., description="Lý do đề xuất câu hỏi này")

    model_config = {"from_attributes": True}


# ======================== Mastery Schemas ========================

class LearnerMasteryResponse(BaseModel):
    """Schema phản hồi mức độ thành thạo theo chủ đề."""
    topic_id: int
    topic_name: str
    subject_name: str
    mastery_score: float
    elo_rating: float
    total_attempts: int
    correct_attempts: int
    bloom_level: int
    last_practiced: Optional[datetime]

    model_config = {"from_attributes": True}
