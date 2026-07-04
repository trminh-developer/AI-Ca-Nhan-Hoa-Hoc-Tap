"""
Thiết lập kết nối cơ sở dữ liệu SQLAlchemy với SQL Server qua pymssql.
"""

try:
    import pymssql
except ImportError:
    pass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL, DB_SERVER, DB_USER, DB_PASSWORD, DB_NAME


def create_database_if_not_exists():
    """Tạo database AdaptiveLearningDB nếu chưa tồn tại trên SQL Server."""
    pass


# Tạo engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class cho tất cả các models SQLAlchemy."""
    pass


def get_db():
    """
    Dependency để inject database session vào các route handlers.
    Tự động đóng session sau khi request hoàn tất.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Tạo tất cả các bảng trong cơ sở dữ liệu."""
    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
