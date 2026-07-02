"""
Thiết lập kết nối cơ sở dữ liệu SQLAlchemy với SQL Server qua pymssql.
"""

import pymssql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL, DB_SERVER, DB_USER, DB_PASSWORD, DB_NAME


def create_database_if_not_exists():
    """Tạo database AdaptiveLearningDB nếu chưa tồn tại trên SQL Server."""
    pass


# Tạo engine
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Đặt True để debug SQL queries
)

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
