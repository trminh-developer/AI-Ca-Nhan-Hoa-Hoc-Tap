"""
Model Người dùng (User) - Lưu trữ thông tin tài khoản và Elo tổng thể.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean

from database import Base


class User(Base):
    """
    Bảng người dùng - lưu thông tin đăng nhập và điểm Elo tổng thể.
    
    Attributes:
        id: Khóa chính
        username: Tên đăng nhập (duy nhất)
        email: Email (duy nhất)
        hashed_password: Mật khẩu đã được hash
        overall_elo: Điểm Elo tổng thể (mặc định 1500)
        created_at: Thời điểm tạo tài khoản
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    overall_elo = Column(Float, default=1500.0, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', elo={self.overall_elo})>"
