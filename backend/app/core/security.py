"""
Security & Authentication Module (Python 3.14.x).
Bao gồm:
- Bcrypt password hashing & verification
- JWT Access Token & Refresh Token Rotation (SHA-256 hashed persistence)
- RBAC FastAPI Dependencies (Student, Teacher, Admin)
"""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from app.db.session import get_db
from app.models.user import RefreshToken, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác minh mật khẩu gốc với mật khẩu đã băm."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def hash_refresh_token(raw_token: str) -> str:
    """Băm SHA-256 cho Refresh Token trước khi lưu xuống Database."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Tạo JWT Access Token ngắn hạn kèm metadata loại token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(db: Session, user_id: int) -> str:
    """
    Sinh Refresh Token ngẫu nhiên mật mã học (URL-safe), lưu bản băm SHA-256 vào DB
    và trả về chuỗi gốc cho Client.
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(db_token)
    db.commit()
    return raw_token


def rotate_refresh_token(db: Session, raw_refresh_token: str) -> tuple[User, str, str]:
    """
    Xác thực Refresh Token, thu hồi (revoke) token cũ và cấp cặp (Access Token, Refresh Token) mới.
    """
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not raw_refresh_token:
        raise invalid_exc

    token_hash = hash_refresh_token(raw_refresh_token.strip())
    record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
        .first()
    )
    if not record:
        raise invalid_exc

    now_utc = datetime.now(timezone.utc)
    exp = record.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp <= now_utc:
        record.revoked = True
        db.commit()
        raise invalid_exc

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        record.revoked = True
        db.commit()
        raise invalid_exc

    # Thu hồi token cũ (Rotation)
    record.revoked = True
    db.commit()

    new_access = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    new_refresh = create_refresh_token(db, user.id)
    return user, new_access, new_refresh


def revoke_refresh_token(db: Session, raw_refresh_token: str | None) -> bool:
    """Thu hồi một Refresh Token khi người dùng đăng xuất."""
    if not raw_refresh_token:
        return False
    token_hash = hash_refresh_token(raw_refresh_token.strip())
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not record:
        return False
    record.revoked = True
    db.commit()
    return True


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Giải mã JWT Access Token và trả về payload (hoặc None nếu không hợp lệ)."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI Dependency giải mã JWT Access Token và trả về đối tượng User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Đảm bảo người dùng hiện tại có quyền Quản trị viên (admin)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này (yêu cầu quyền Admin)",
        )
    return current_user


def get_current_teacher_or_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Đảm bảo người dùng hiện tại là Giảng viên (teacher) hoặc Quản trị viên (admin)."""
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này (yêu cầu quyền Admin hoặc Giảng viên)",
        )
    return current_user
