"""
Admin Router - Xử lý các nghiệp vụ quản trị hệ thống.
Chỉ cho phép tài khoản có quyền Admin (is_admin=True) truy cập.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.content import Subject, Topic, Question
from schemas.user import UserResponse
from services.auth_service import get_current_admin_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_admin_user)])


class AdminStats(BaseModel):
    total_users: int
    total_subjects: int
    total_topics: int
    total_questions: int


class RoleUpdate(BaseModel):
    is_admin: bool


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(db: Session = Depends(get_db)):
    """Lấy thống kê tổng quan cho trang Dashboard Admin."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_subjects = db.query(func.count(Subject.id)).scalar() or 0
    total_topics = db.query(func.count(Topic.id)).scalar() or 0
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    
    return AdminStats(
        total_users=total_users,
        total_subjects=total_subjects,
        total_topics=total_topics,
        total_questions=total_questions
    )


@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả người dùng."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """Cấp hoặc thu hồi quyền Admin của một người dùng."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    user.is_admin = role_data.is_admin
    db.commit()
    db.refresh(user)
    return user
