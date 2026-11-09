"""
Models Nội dung học tập - Subject, Topic, ContentItem, Question (Python 3.14.x).
"""

from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Subject(Base):
    """Bảng Môn học."""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_emoji = Column(String(10), default="📚")

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}')>"


class Topic(Base):
    """Bảng Chủ đề gắn với 6 bậc nhận thức Bloom's Revised Taxonomy."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    bloom_level = Column(Integer, default=1, nullable=False)  # 1..6
    order_index = Column(Integer, default=0, nullable=False)
    prerequisites = Column(Text, default="[]")  # JSON array of prerequisite topic IDs

    subject = relationship("Subject", back_populates="topics")
    content_items = relationship("ContentItem", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, name='{self.name}', bloom={self.bloom_level})>"


class ContentItem(Base):
    """Bảng Nội dung lý thuyết & bài tập mẫu."""

    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content_type = Column(String(20), default="lesson", nullable=False)
    body = Column(Text, nullable=True)
    difficulty_elo = Column(Float, default=1500.0, nullable=False)
    bloom_level = Column(Integer, default=1, nullable=False)
    hints = Column(Text, default="[]")

    topic = relationship("Topic", back_populates="content_items")


class Question(Base):
    """Bảng Câu hỏi trắc nghiệm 4 lựa chọn A/B/C/D hỗ trợ LaTeX & Code Snippets."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty_elo = Column(Float, default=1500.0, nullable=False)
    bloom_level = Column(Integer, default=1, nullable=False)

    topic = relationship("Topic", back_populates="questions")

    __table_args__ = (
        Index("ix_questions_topic_elo_bloom", "topic_id", "difficulty_elo", "bloom_level"),
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, elo={self.difficulty_elo}, bloom={self.bloom_level})>"
