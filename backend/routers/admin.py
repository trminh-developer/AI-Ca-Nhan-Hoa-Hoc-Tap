"""
Admin Router - Xử lý các nghiệp vụ quản trị hệ thống.
Hỗ trợ cả phân quyền Admin và Giảng viên.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.content import Subject, Topic, Question
from schemas.user import UserResponse
from schemas.content import QuestionCreate, QuestionResponse
from services.auth_service import get_current_teacher_or_admin_user, get_current_admin_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_teacher_or_admin_user)])


class AdminStats(BaseModel):
    total_users: int
    total_subjects: int
    total_topics: int
    total_questions: int


class RoleUpdate(BaseModel):
    role: str


class TeacherUpdate(BaseModel):
    teacher_id: int | None


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Lấy thống kê tổng quan cho trang Dashboard Admin."""
    if current_user.role == 'admin':
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_questions = db.query(func.count(Question.id)).scalar() or 0
    else:
        total_users = db.query(func.count(User.id)).filter(User.teacher_id == current_user.id).scalar() or 0
        total_questions = db.query(func.count(Question.id)).filter(Question.created_by_id == current_user.id).scalar() or 0
        
    total_subjects = db.query(func.count(Subject.id)).scalar() or 0
    total_topics = db.query(func.count(Topic.id)).scalar() or 0
    
    return AdminStats(
        total_users=total_users,
        total_subjects=total_subjects,
        total_topics=total_topics,
        total_questions=total_questions
    )


@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Lấy danh sách người dùng. Admin xem tất cả, Teacher xem học viên của mình."""
    if current_user.role == 'admin':
        return db.query(User).order_by(User.created_at.desc()).all()
    else:
        return db.query(User).filter(User.teacher_id == current_user.id).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/role", response_model=UserResponse, dependencies=[Depends(get_current_admin_user)])
def update_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """Cấp quyền cho người dùng (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if role_data.role not in ['admin', 'teacher', 'student']:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")
        
    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/teacher", response_model=UserResponse, dependencies=[Depends(get_current_admin_user)])
def assign_teacher(user_id: int, teacher_data: TeacherUpdate, db: Session = Depends(get_db)):
    """Chỉ định giảng viên cho học viên (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    if teacher_data.teacher_id is not None:
        teacher = db.query(User).filter(User.id == teacher_data.teacher_id, User.role == 'teacher').first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Giảng viên không tồn tại")
            
    user.teacher_id = teacher_data.teacher_id
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Xóa người dùng (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
        
    # Xử lý các liên kết trước khi xóa (set null)
    if user.role == 'teacher':
        db.query(User).filter(User.teacher_id == user.id).update({User.teacher_id: None})
        db.query(Question).filter(Question.created_by_id == user.id).update({Question.created_by_id: None})
        
    db.delete(user)
    db.commit()
    return {"message": "Đã xóa người dùng thành công"}


@router.get("/questions", response_model=list[QuestionResponse])
def get_questions(db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Lấy danh sách bài quiz. Admin xem tất cả, Teacher xem của mình."""
    if current_user.role == 'admin':
        return db.query(Question).all()
    else:
        return db.query(Question).filter(Question.created_by_id == current_user.id).all()


@router.post("/questions", response_model=QuestionResponse)
def create_question(q_in: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Tạo bài quiz mới."""
    topic = db.query(Topic).filter(Topic.id == q_in.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Chủ đề không tồn tại")
        
    new_q = Question(**q_in.model_dump(), created_by_id=current_user.id)
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, q_in: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Sửa bài quiz."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Câu hỏi không tồn tại")
        
    if current_user.role != 'admin' and q.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền sửa câu hỏi của người khác")
        
    for key, value in q_in.model_dump().items():
        setattr(q, key, value)
        
    db.commit()
    db.refresh(q)
    return q


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher_or_admin_user)):
    """Xóa bài quiz."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Câu hỏi không tồn tại")
        
    if current_user.role != 'admin' and q.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền xóa câu hỏi của người khác")
        
    db.delete(q)
    db.commit()
    return {"message": "Đã xóa thành công"}
