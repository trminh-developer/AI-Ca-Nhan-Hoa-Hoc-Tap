from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base

class ChatHistory(Base):
    """
    Bảng Lịch sử Chat - lưu lại hội thoại giữa User và Chatbot AI.
    
    Attributes:
        id: Khóa chính
        user_id: Người chat
        role: Vai trò ('user' hoặc 'model')
        message: Nội dung chat
        created_at: Thời gian
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(10), nullable=False) # 'user' or 'model'
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self):
        return f"<ChatHistory(user={self.user_id}, role='{self.role}', time='{self.created_at}')>"
