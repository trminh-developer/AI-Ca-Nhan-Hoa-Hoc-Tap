"""Pydantic v2 Schemas cho Nội dung học tập (Subject, Topic, Question, ContentItem)."""

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    icon_emoji: str = Field("📚", max_length=10)


class SubjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon_emoji: str
    topic_count: int = 0

    model_config = {"from_attributes": True}


class TopicCreate(BaseModel):
    subject_id: int
    name: str = Field(..., max_length=200)
    description: str | None = None
    bloom_level: int = Field(1, ge=1, le=6)
    order_index: int = 0
    prerequisites: list[int] = Field(default_factory=list)


class TopicResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    description: str | None
    bloom_level: int
    order_index: int
    prerequisites: list[int]
    question_count: int = 0

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str = Field(..., pattern="^[abcd]$")
    explanation: str | None = None
    difficulty_elo: float = 1500.0
    bloom_level: int = Field(1, ge=1, le=6)


class QuestionResponse(BaseModel):
    id: int
    topic_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str | None
    difficulty_elo: float
    bloom_level: int
    created_by_id: int | None = None

    model_config = {"from_attributes": True}


class QuestionPublic(BaseModel):
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


class ContentItemCreate(BaseModel):
    topic_id: int
    title: str = Field(..., max_length=300)
    content_type: str = Field("lesson", pattern="^(lesson|exercise)$")
    body: str | None = None
    difficulty_elo: float = 1500.0
    bloom_level: int = Field(1, ge=1, le=6)
    hints: list[str] = Field(default_factory=list)


class ContentItemResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    content_type: str
    body: str | None
    difficulty_elo: float
    bloom_level: int
    hints: list[str]

    model_config = {"from_attributes": True}
