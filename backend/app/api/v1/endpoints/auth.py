"""
Authentication Endpoints - Đăng ký, Đăng nhập (Access + Refresh Token), Làm mới phiên, Đăng xuất và Hồ sơ.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản học viên mới với điểm Elo khởi tạo mặc định (1500.0).
    """
    clean_username = user_data.username.strip()
    clean_email = user_data.email.strip().lower()

    existing_user = db.query(User).filter(User.username == clean_username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{clean_username}' đã được sử dụng",
        )

    existing_email = db.query(User).filter(User.email == clean_email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{clean_email}' đã được sử dụng",
        )

    new_user = User(
        username=clean_username,
        email=clean_email,
        hashed_password=hash_password(user_data.password),
        overall_elo=settings.DEFAULT_ELO,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Đăng nhập bằng username hoặc email, trả về bộ đôi JWT `access_token` và `refresh_token`.
    """
    identifier = form_data.username.strip()
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == identifier,
                User.email == identifier.lower(),
            )
        )
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    raw_refresh_token = create_refresh_token(db, user.id)

    return Token(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
    )


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Làm mới `access_token` bằng `refresh_token` hợp lệ và thực hiện Token Rotation.
    """
    user, new_access_token, new_refresh_token = rotate_refresh_token(
        db=db,
        raw_refresh_token=payload.refresh_token,
    )
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
    )


@router.post("/logout")
def logout(
    payload: RefreshTokenRequest | None = None,
    db: Session = Depends(get_db),
):
    """
    Đăng xuất và thu hồi `refresh_token` trong cơ sở dữ liệu.
    """
    revoked = False
    if payload and payload.refresh_token:
        revoked = revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Đăng xuất thành công", "revoked": revoked}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin hồ sơ người dùng hiện tại."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật email hoặc mật khẩu của người dùng hiện tại."""
    if user_data.email is not None:
        clean_email = user_data.email.strip().lower()
        existing_email = (
            db.query(User)
            .filter(User.email == clean_email, User.id != current_user.id)
            .first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng")
        current_user.email = clean_email

    if user_data.password is not None:
        current_user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(current_user)
    return current_user
