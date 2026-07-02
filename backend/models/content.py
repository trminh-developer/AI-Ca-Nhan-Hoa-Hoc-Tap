"""
Models Nội dung học tập - Quản lý môn học, chủ đề, bài học và câu hỏi.
"""

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Subject(Base):
    """
    Bảng Môn học - phân loại nội dung theo môn.
    
    Attributes:
        id: Khóa chính
        name: Tên môn học
        description: Mô tả môn học
        icon_emoji: Emoji đại diện cho môn học
    """
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_emoji = Column(String(10), default="📚")

    # Quan hệ: một môn học có nhiều chủ đề
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}')>"


class Topic(Base):
    """
    Bảng Chủ đề - các chủ đề trong mỗi môn học, sắp xếp theo Bloom's Taxonomy.
    
    Attributes:
        id: Khóa chính
        subject_id: FK đến môn học
        name: Tên chủ đề
        description: Mô tả chủ đề
        bloom_level: Cấp độ Bloom (1=Nhớ, 2=Hiểu, 3=Áp dụng, 4=Phân tích, 5=Đánh giá, 6=Sáng tạo)
        order_index: Thứ tự hiển thị trong môn học
        prerequisites: Danh sách ID các chủ đề tiên quyết (JSON)
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    bloom_level = Column(Integer, default=1, nullable=False)  # 1-6
    order_index = Column(Integer, default=0, nullable=False)
    prerequisites = Column(Text, default="[]")  # JSON string: danh sách topic_id tiên quyết

    # Quan hệ
    subject = relationship("Subject", back_populates="topics")
    content_items = relationship("ContentItem", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', bloom={self.bloom_level})>"


class ContentItem(Base):
    """
    Bảng Nội dung học tập - bài học và bài tập.
    
    Attributes:
        id: Khóa chính
        topic_id: FK đến chủ đề
        title: Tiêu đề
        content_type: Loại nội dung ('lesson' hoặc 'exercise')
        body: Nội dung chi tiết (HTML/Markdown)
        difficulty_elo: Độ khó theo thang Elo
        bloom_level: Cấp độ Bloom
        hints: Danh sách gợi ý (JSON)
    """
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(300), nullable=False)
    content_type = Column(String(20), default="lesson", nullable=False)  # 'lesson' | 'exercise'
    body = Column(Text, nullable=True)
    difficulty_elo = Column(Float, default=1500.0, nullable=False)
    bloom_level = Column(Integer, default=1, nullable=False)
    hints = Column(Text, default="[]")  # JSON string: danh sách các gợi ý

    # Quan hệ
    topic = relationship("Topic", back_populates="content_items")

    def __repr__(self):
        return f"<ContentItem(id={self.id}, title='{self.title}', type='{self.content_type}')>"


class Question(Base):
    """
    Bảng Câu hỏi trắc nghiệm - 4 phương án A/B/C/D.
    
    Attributes:
        id: Khóa chính
        topic_id: FK đến chủ đề
        question_text: Nội dung câu hỏi
        option_a/b/c/d: 4 phương án trả lời
        correct_answer: Đáp án đúng ('a', 'b', 'c', hoặc 'd')
        explanation: Giải thích đáp án
        difficulty_elo: Độ khó theo thang Elo
        bloom_level: Cấp độ Bloom (1-6)
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # 'a', 'b', 'c', 'd'
    explanation = Column(Text, nullable=True)
    difficulty_elo = Column(Float, default=1500.0, nullable=False)
    bloom_level = Column(Integer, default=1, nullable=False)

    # Quan hệ
    topic = relationship("Topic", back_populates="questions")

    def __repr__(self):
        return f"<Question(id={self.id}, elo={self.difficulty_elo}, bloom={self.bloom_level})>"
