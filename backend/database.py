"""
Root Database Compatibility Layer - Re-exports from `app.db.session` and `app.db.base`.
"""

from app.db.base import Base
from app.db.session import SessionLocal, create_tables, engine, ensure_schema_columns, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db", "create_tables", "ensure_schema_columns"]
