"""
Pydantic Schemas cho Học tập thích ứng - Submit/Result, Quiz, Progress, Mastery, Analytics & SM-2.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AnswerSubmit(BaseModel):
    """Schema gửi câu trả lời."""

    question_id: int = Field(..., description="ID câu hỏi")
    selected_answer: str = Field(..., pattern="^[abcdABCD]$", description="Đáp án được chọn (a/b/c/d)")
    time_spent_ms: int = Field(0, ge=0, description="Thời gian trả lời (ms)")
    hints_used: int = Field(0, ge=0, le=5, description="Số lần dùng gợi ý Socratic")


class AnswerResult(BaseModel):
    """Schema kết quả sau khi trả lời."""

    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    elo_change: float = Field(..., description="Thay đổi Elo (+/-)")
    new_elo: float = Field(..., description="Elo mới sau khi trả lời")
    xp_earned: int = Field(0, description="Điểm kinh nghiệm nhận được")
    sm2_quality: int = Field(4, description="Điểm chất lượng nhớ SM-2 (0-5)")
    next_review_days: int = Field(1, description="Số ngày đến lần ôn tập tiếp theo")
    easiness_factor: float = Field(2.5, description="Hệ số dễ EF mới")


class QuizStart(BaseModel):
    """Schema bắt đầu phiên làm bài thích ứng ZPD."""

    topic_id: int = Field(..., description="ID chủ đề")
    num_questions: int = Field(10, ge=1, le=50, description="Số câu hỏi")


QuizStartRequest = QuizStart


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
    selected_answer: str = Field(..., pattern="^[abcdABCD]$")
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


class TopicMasteryItem(BaseModel):
    """Schema thông tin thành thạo cho một chủ đề."""

    topic_id: int
    topic_name: str
    subject_id: Optional[int] = None
    subject_name: str = ""
    bloom_level: int = 1
    mastery_score: float
    elo_rating: float
    total_attempts: int
    correct_attempts: int
    accuracy: float = Field(..., description="Tỉ lệ đúng cho chủ đề")
    last_practiced: Optional[datetime] = None


class EloHistoryPoint(BaseModel):
    """Một điểm dữ liệu trên biểu đồ biến thiên Elo theo thời gian."""

    index: int
    elo: float
    change: float = 0.0
    delta: float = 0.0
    is_correct: bool
    timestamp: str


class BloomRadarPoint(BaseModel):
    """Một đỉnh trên biểu đồ Radar 6 cấp độ nhận thức Bloom."""

    bloom_level: int = 1
    level: int = 1
    label: str
    mastery_percent: float = 0.0
    mastery: float = 0.0
    unlocked: bool = True
    questions_attempted: int = 0
    attempts: int = 0


class ProgressResponse(BaseModel):
    """Schema tổng quan tiến độ học tập kèm biểu đồ Elo & Bloom Radar."""

    overall_elo: float
    topics_mastery: list[TopicMasteryItem]
    total_questions_answered: int
    accuracy_rate: float = Field(..., description="Tỉ lệ đúng tổng thể")
    current_streak: int = Field(0, description="Chuỗi trả lời đúng liên tiếp hiện tại")
    elo_history: list[EloHistoryPoint] = Field(default_factory=list)
    bloom_radar: list[BloomRadarPoint] = Field(default_factory=list)
    due_reviews_count: int = Field(0, description="Số thẻ SM-2 đến hạn ôn tập hôm nay")


class NextQuestionResponse(BaseModel):
    """Schema câu hỏi được đề xuất tiếp theo trong vùng ZPD."""

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
    last_practiced: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SpacedReviewCard(BaseModel):
    """Schema thẻ Flashcard ôn tập ngắt quãng SM-2."""

    id: int
    topic_id: int
    topic_name: str = ""
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty_elo: float
    bloom_level: int
    repetitions: int = 0
    interval_days: int = 1
    easiness_factor: float = 2.5
    next_review: Optional[datetime] = None

    model_config = {"from_attributes": True}
