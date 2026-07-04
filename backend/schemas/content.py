"""
Pydantic Schemas cho Nội dung học tập - Subject, Topic, Question, ContentItem.
"""

from typing import Optional

from pydantic import BaseModel, Field


# ======================== Subject Schemas ========================

class SubjectCreate(BaseModel):
    """Schema tạo môn học mới."""
    name: str = Field(..., max_length=100, description="Tên môn học")
    description: Optional[str] = Field(None, description="Mô tả môn học")
    icon_emoji: str = Field("📚", max_length=10, description="Emoji đại diện")


class SubjectResponse(BaseModel):
    """Schema phản hồi thông tin môn học."""
    id: int
    name: str
    description: Optional[str]
    icon_emoji: str
    topic_count: int = 0  # Số chủ đề trong môn học

    model_config = {"from_attributes": True}


# ======================== Topic Schemas ========================

class TopicCreate(BaseModel):
    """Schema tạo chủ đề mới."""
    subject_id: int = Field(..., description="ID môn học")
    name: str = Field(..., max_length=200, description="Tên chủ đề")
    description: Optional[str] = Field(None, description="Mô tả chủ đề")
    bloom_level: int = Field(1, ge=1, le=6, description="Cấp độ Bloom (1-6)")
    order_index: int = Field(0, description="Thứ tự hiển thị")
    prerequisites: list[int] = Field(default_factory=list, description="Danh sách ID chủ đề tiên quyết")


class TopicResponse(BaseModel):
    """Schema phản hồi thông tin chủ đề."""
    id: int
    subject_id: int
    name: str
    description: Optional[str]
    bloom_level: int
    order_index: int
    prerequisites: list[int]
    question_count: int = 0  # Số câu hỏi trong chủ đề

    model_config = {"from_attributes": True}


# ======================== Question Schemas ========================

class QuestionCreate(BaseModel):
    """Schema tạo câu hỏi mới."""
    topic_id: int = Field(..., description="ID chủ đề")
    question_text: str = Field(..., description="Nội dung câu hỏi")
    option_a: str = Field(..., description="Phương án A")
    option_b: str = Field(..., description="Phương án B")
    option_c: str = Field(..., description="Phương án C")
    option_d: str = Field(..., description="Phương án D")
    correct_answer: str = Field(..., pattern="^[abcd]$", description="Đáp án đúng (a/b/c/d)")
    explanation: Optional[str] = Field(None, description="Giải thích đáp án")
    difficulty_elo: float = Field(1500.0, description="Độ khó Elo")
    bloom_level: int = Field(1, ge=1, le=6, description="Cấp độ Bloom")


class QuestionResponse(BaseModel):
    """Schema phản hồi câu hỏi (bao gồm đáp án - dùng cho admin)."""
    id: int
    topic_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str]
    difficulty_elo: float
    bloom_level: int
    created_by_id: int | None = None

    model_config = {"from_attributes": True}


class QuestionPublic(BaseModel):
    """Schema câu hỏi cho học sinh (KHÔNG bao gồm đáp án đúng)."""
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


# ======================== ContentItem Schemas ========================

class ContentItemCreate(BaseModel):
    """Schema tạo nội dung học tập mới."""
    topic_id: int = Field(..., description="ID chủ đề")
    title: str = Field(..., max_length=300, description="Tiêu đề")
    content_type: str = Field("lesson", pattern="^(lesson|exercise)$", description="Loại nội dung")
    body: Optional[str] = Field(None, description="Nội dung chi tiết")
    difficulty_elo: float = Field(1500.0, description="Độ khó Elo")
    bloom_level: int = Field(1, ge=1, le=6, description="Cấp độ Bloom")
    hints: list[str] = Field(default_factory=list, description="Danh sách gợi ý")


class ContentItemResponse(BaseModel):
    """Schema phản hồi nội dung học tập."""
    id: int
    topic_id: int
    title: str
    content_type: str
    body: Optional[str]
    difficulty_elo: float
    bloom_level: int
    hints: list[str]

    model_config = {"from_attributes": True}
