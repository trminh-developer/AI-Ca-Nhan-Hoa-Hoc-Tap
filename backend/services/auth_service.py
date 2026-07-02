"""
Auth Service - Xác thực và phân quyền người dùng.

Bao gồm:
- Hash và verify mật khẩu (bcrypt)
- Tạo và xác thực JWT token
- Dependency get_current_user cho FastAPI
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models.user import User

# OAuth2 scheme - lấy token từ header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """
    Hash mật khẩu bằng bcrypt.
    
    Args:
        password: Mật khẩu gốc
        
    Returns:
        Mật khẩu đã được hash
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác minh mật khẩu gốc với mật khẩu đã hash.
    
    Args:
        plain_password: Mật khẩu gốc
        hashed_password: Mật khẩu đã hash trong DB
        
    Returns:
        True nếu khớp, False nếu không
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Tạo JWT access token.
    
    Args:
        data: Dữ liệu payload (thường là {"sub": username})
        expires_delta: Thời gian hết hạn (mặc định từ config)
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI Dependency - Lấy user hiện tại từ JWT token.
    
    Quy trình:
    1. Decode JWT token
    2. Lấy username từ payload
    3. Truy vấn DB để lấy user
    4. Trả về User object hoặc raise 401
    
    Args:
        token: JWT token từ header Authorization
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException 401: Token không hợp lệ hoặc user không tồn tại
    """
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
    """
    FastAPI Dependency - Đảm bảo user hiện tại là Admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này (yêu cầu quyền Admin)",
        )
    return current_user
