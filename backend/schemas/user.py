"""
Pydantic Schemas cho User - Xác thực dữ liệu đầu vào/đầu ra liên quan đến người dùng.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema tạo tài khoản mới."""
    username: str = Field(..., min_length=3, max_length=50, description="Tên đăng nhập")
    email: EmailStr = Field(..., description="Địa chỉ email")
    password: str = Field(..., min_length=6, max_length=128, description="Mật khẩu")


class UserLogin(BaseModel):
    """Schema đăng nhập."""
    username: str = Field(..., description="Tên đăng nhập")
    password: str = Field(..., description="Mật khẩu")


class UserUpdate(BaseModel):
    """Schema cập nhật thông tin."""
    email: EmailStr | None = Field(None, description="Địa chỉ email mới")
    password: str | None = Field(None, min_length=6, max_length=128, description="Mật khẩu mới")


class UserResponse(BaseModel):
    """Schema phản hồi thông tin người dùng (không bao gồm mật khẩu)."""
    id: int
    username: str
    email: str
    overall_elo: float
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema phản hồi JWT token."""
    access_token: str
    token_type: str = "bearer"
