"""
Auth Router - Xử lý đăng ký, đăng nhập và xác thực người dùng.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token, UserUpdate
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới.
    
    - Kiểm tra username và email chưa tồn tại
    - Hash mật khẩu bằng bcrypt
    - Tạo user mới với Elo mặc định 1500
    """
    # Kiểm tra username đã tồn tại
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{user_data.username}' đã được sử dụng",
        )
    
    # Kiểm tra email đã tồn tại
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' đã được sử dụng",
        )
    
    # Tạo user mới
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Đăng nhập và nhận JWT token.
    
    - Xác thực username và mật khẩu
    - Trả về access_token (JWT) nếu thành công
    """
    # Tìm user theo username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Xác thực mật khẩu
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Tạo JWT token
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng hiện tại.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Cập nhật thông tin cá nhân.
    """
    if user_data.email is not None:
        existing_email = db.query(User).filter(User.email == user_data.email, User.id != current_user.id).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
        current_user.email = user_data.email
        
    if user_data.password is not None:
        current_user.hashed_password = hash_password(user_data.password)
        
    db.commit()
    db.refresh(current_user)
    return current_user
