"""
Admin & Teacher Hub Endpoints - Quản trị người dùng, phân quyền RBAC, Ngân hàng câu hỏi và Cấu hình thuật toán.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_admin_user,
    get_current_teacher_or_admin_user,
)
from app.db.session import get_db
from app.models.content import Question, Subject, Topic
from app.models.user import SystemConfig, User
from app.schemas.content import QuestionCreate, QuestionResponse
from app.schemas.user import UserResponse
from app.services.elo_service import elo_engine
from app.services.zpd_service import ZPD_LOWER_PROB, ZPD_UPPER_PROB

router = APIRouter(
    prefix="/admin",
    tags=["Admin & Teacher Hub"],
    dependencies=[Depends(get_current_teacher_or_admin_user)],
)


class AdminStats(BaseModel):
    total_users: int
    total_subjects: int
    total_topics: int
    total_questions: int


class RoleUpdate(BaseModel):
    role: str


class TeacherUpdate(BaseModel):
    teacher_id: int | None


class AlgorithmConfigPayload(BaseModel):
    k_learner: float = Field(default=32.0, ge=4.0, le=128.0)
    k_item: float = Field(default=16.0, ge=2.0, le=64.0)
    zpd_lower_prob: float = Field(default=0.60, ge=0.30, le=0.75)
    zpd_upper_prob: float = Field(default=0.75, ge=0.60, le=0.95)


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Lấy thống kê tổng quan cho trang Dashboard Admin/Giảng viên."""
    if current_user.role == "admin":
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_questions = db.query(func.count(Question.id)).scalar() or 0
    else:
        total_users = (
            db.query(func.count(User.id))
            .filter(User.teacher_id == current_user.id)
            .scalar()
            or 0
        )
        total_questions = (
            db.query(func.count(Question.id))
            .filter(Question.created_by_id == current_user.id)
            .scalar()
            or 0
        )

    total_subjects = db.query(func.count(Subject.id)).scalar() or 0
    total_topics = db.query(func.count(Topic.id)).scalar() or 0

    return AdminStats(
        total_users=total_users,
        total_subjects=total_subjects,
        total_topics=total_topics,
        total_questions=total_questions,
    )


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Lấy danh sách người dùng. Admin xem tất cả, Teacher xem học viên được phân công."""
    if current_user.role == "admin":
        return db.query(User).order_by(User.created_at.desc()).all()
    return (
        db.query(User)
        .filter(User.teacher_id == current_user.id)
        .order_by(User.created_at.desc())
        .all()
    )


@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def update_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """Cấp quyền cho người dùng (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if role_data.role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user


@router.put(
    "/users/{user_id}/teacher",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin_user)],
)
def assign_teacher(
    user_id: int,
    teacher_data: TeacherUpdate,
    db: Session = Depends(get_db),
):
    """Chỉ định giảng viên hướng dẫn cho học viên (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    if teacher_data.teacher_id is not None:
        teacher = (
            db.query(User)
            .filter(User.id == teacher_data.teacher_id, User.role == "teacher")
            .first()
        )
        if not teacher:
            raise HTTPException(status_code=404, detail="Giảng viên không tồn tại")

    user.teacher_id = teacher_data.teacher_id
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Xóa người dùng và gỡ liên kết khóa ngoại an toàn (Chỉ Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    if user.role == "teacher":
        db.query(User).filter(User.teacher_id == user.id).update({User.teacher_id: None})
        db.query(Question).filter(Question.created_by_id == user.id).update(
            {Question.created_by_id: None}
        )

    db.delete(user)
    db.commit()
    return {"message": "Đã xóa người dùng thành công"}


@router.get("/questions", response_model=list[QuestionResponse])
def get_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Lấy danh sách câu hỏi. Admin xem toàn hệ thống, Teacher xem câu hỏi do mình tạo."""
    if current_user.role == "admin":
        return db.query(Question).order_by(Question.id.desc()).all()
    return (
        db.query(Question)
        .filter(Question.created_by_id == current_user.id)
        .order_by(Question.id.desc())
        .all()
    )


@router.post("/questions", response_model=QuestionResponse)
def create_question(
    q_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Tạo câu hỏi trắc nghiệm mới."""
    topic = db.query(Topic).filter(Topic.id == q_in.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Chủ đề không tồn tại")

    new_q = Question(**q_in.model_dump(), created_by_id=current_user.id)
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    q_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Cập nhật nội dung câu hỏi."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Câu hỏi không tồn tại")

    if current_user.role != "admin" and q.created_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Không có quyền sửa câu hỏi của người khác"
        )

    for key, value in q_in.model_dump().items():
        setattr(q, key, value)

    db.commit()
    db.refresh(q)
    return q


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin_user),
):
    """Xóa câu hỏi."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Câu hỏi không tồn tại")

    if current_user.role != "admin" and q.created_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Không có quyền xóa câu hỏi của người khác"
        )

    db.delete(q)
    db.commit()
    return {"message": "Đã xóa thành công"}


@router.get("/config", response_model=AlgorithmConfigPayload)
def get_algorithm_config(db: Session = Depends(get_db)):
    """Lấy thông số cấu hình thuật toán Dual Elo & ZPD hiện tại."""
    configs = {c.key: c.value for c in db.query(SystemConfig).all()}
    return AlgorithmConfigPayload(
        k_learner=float(configs.get("k_learner", elo_engine.k_learner)),
        k_item=float(configs.get("k_item", elo_engine.k_item)),
        zpd_lower_prob=float(configs.get("zpd_lower_prob", ZPD_LOWER_PROB)),
        zpd_upper_prob=float(configs.get("zpd_upper_prob", ZPD_UPPER_PROB)),
    )


@router.put(
    "/config",
    response_model=AlgorithmConfigPayload,
    dependencies=[Depends(get_current_admin_user)],
)
def update_algorithm_config(
    payload: AlgorithmConfigPayload,
    db: Session = Depends(get_db),
):
    """Cập nhật hệ số K-factor và ngưỡng ZPD của hệ thống (Chỉ Admin)."""
    elo_engine.k_learner = payload.k_learner
    elo_engine.k_item = payload.k_item

    entries = {
        "k_learner": (str(payload.k_learner), "Hệ số K cho học viên (Dual Elo)"),
        "k_item": (str(payload.k_item), "Hệ số K cho câu hỏi (Dual Elo)"),
        "zpd_lower_prob": (str(payload.zpd_lower_prob), "Ngưỡng xác suất ZPD dưới"),
        "zpd_upper_prob": (str(payload.zpd_upper_prob), "Ngưỡng xác suất ZPD trên"),
    }
    for key, (val, desc) in entries.items():
        record = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if record:
            record.value = val
        else:
            db.add(SystemConfig(key=key, value=val, description=desc))

    db.commit()
    return payload


@router.post("/seed", dependencies=[Depends(get_current_admin_user)])
def trigger_seed_database(db: Session = Depends(get_db)):
    """Khởi tạo / đồng bộ bộ dữ liệu mẫu NCKH chuẩn (3 môn x 4 chủ đề x 10 câu hỏi + tài khoản RBAC)."""
    from seed_data import seed_all

    summary = seed_all(db)
    return {
        "message": "Đã đồng bộ dữ liệu mẫu chuẩn NCKH thành công!",
        "summary": summary,
    }

