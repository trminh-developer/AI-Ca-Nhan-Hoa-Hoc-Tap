"""Pydantic v2 Schemas cho Người dùng & Xác thực JWT (Access + Refresh Token)."""

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
    """Schema cập nhật thông tin cá nhân."""

    email: EmailStr | None = Field(None, description="Địa chỉ email mới")
    password: str | None = Field(None, min_length=6, max_length=128, description="Mật khẩu mới")


class UserResponse(BaseModel):
    """Schema phản hồi thông tin người dùng."""

    id: int
    username: str
    email: str
    overall_elo: float
    role: str
    teacher_id: int | None = None
    created_at: datetime

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema phản hồi cặp JWT Access Token & Refresh Token."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = 3600
    role: str | None = None


class TokenData(BaseModel):
    """Schema dữ liệu giải mã từ JWT payload."""

    username: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema yêu cầu làm mới Access Token."""

    refresh_token: str = Field(..., min_length=10, description="Refresh token đã cấp khi đăng nhập")


class LogoutRequest(BaseModel):
    """Schema thu hồi Refresh Token khi đăng xuất."""

    refresh_token: str | None = None
