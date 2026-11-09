"""
Quản lý kết nối Cơ sở dữ liệu SQLAlchemy 2.0 (Python 3.14.x).
Hỗ trợ cả PostgreSQL (Supabase) và SQLite với cơ chế kiểm tra schema tự động.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL
from app.db.base import Base

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp Database Session cho mỗi HTTP request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema_columns() -> None:
    """
    Đảm bảo các cột nâng cấp (role, teacher_id, created_by_id, hints) tồn tại
    nếu người dùng tái sử dụng file SQLite cũ trước khi chạy Alembic.
    """
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as conn:
        if "users" in table_names:
            user_cols = {col["name"] for col in inspector.get_columns("users")}
            if "role" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student'"))
            if "teacher_id" not in user_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN teacher_id INTEGER NULL"))
        if "questions" in table_names:
            q_cols = {col["name"] for col in inspector.get_columns("questions")}
            if "created_by_id" not in q_cols:
                conn.execute(text("ALTER TABLE questions ADD COLUMN created_by_id INTEGER NULL"))


def create_tables() -> None:
    """Tạo toàn bộ bảng và đồng bộ các cột cần thiết."""
    Base.metadata.create_all(bind=engine)
    ensure_schema_columns()
