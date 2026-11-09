"""
Cấu hình hệ thống Nyvora sử dụng Pydantic-Settings v2 (Python 3.14.x).
Tự động kiểm tra khả năng phân giải DNS của PostgreSQL từ xa và fallback an toàn sang SQLite.
"""

import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ENV_PATH = os.path.join(_BACKEND_DIR, ".env")
load_dotenv(_ENV_PATH)


def _resolve_working_database_url(raw_url: str | None) -> str:
    """
    Chuẩn hóa DATABASE_URL và tự động fallback về SQLite chuẩn hóa nếu host PostgreSQL
    từ xa không thể phân giải DNS (ví dụ: project Supabase Free bị tạm dừng).
    """
    default_sqlite = f"sqlite:///{os.path.join(_BACKEND_DIR, 'nyvora_adaptive.db')}"
    if not raw_url:
        return default_sqlite

    cleaned = raw_url.strip().strip('"').strip("'")
    if cleaned.startswith("postgres://"):
        cleaned = cleaned.replace("postgres://", "postgresql://", 1)

    if cleaned.startswith("postgresql"):
        try:
            parsed = urlparse(cleaned)
            if parsed.hostname:
                socket.getaddrinfo(parsed.hostname, parsed.port or 5432)
        except OSError:
            return default_sqlite

    return cleaned


class Settings(BaseSettings):
    """Cấu hình trung tâm chuẩn Pydantic v2 cho Nyvora Backend."""

    APP_NAME: str = "Nyvora Adaptive Learning Platform API"
    APP_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    DB_SERVER: str = os.getenv("DB_SERVER", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "AdaptiveLearningDB")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    RAW_DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "nyvora-nckh-adaptive-learning-secret-key-production-2026",
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    INITIAL_ELO: float = 1500.0
    DEFAULT_ELO: float = 1500.0
    K_FACTOR: float = 32.0
    K_FACTOR_LEARNER: float = 32.0
    K_FACTOR_STABLE: float = 16.0
    K_FACTOR_ITEM: float = 16.0
    DEFAULT_EASINESS_FACTOR: float = 2.5
    MIN_EASINESS_FACTOR: float = 1.3
    ZPD_LOW: float = 0.60
    ZPD_HIGH: float = 0.75
    GEMINI_FALLBACK_MODELS: list[str] = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://trminh-learningai.vercel.app",
        "https://learningai-f6l8eae4m-trminh-developers-projects.vercel.app",
    ]

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return _resolve_working_database_url(self.RAW_DATABASE_URL)


settings = Settings()

# Xuất các hằng số tương thích ngược cho toàn bộ codebase
DB_SERVER = settings.DB_SERVER
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = settings.GEMINI_MODEL
GEMINI_FALLBACK_MODELS = settings.GEMINI_FALLBACK_MODELS
INITIAL_ELO = settings.INITIAL_ELO
DEFAULT_ELO = settings.DEFAULT_ELO
K_FACTOR = settings.K_FACTOR
K_FACTOR_LEARNER = settings.K_FACTOR_LEARNER
K_FACTOR_ITEM = settings.K_FACTOR_ITEM
DEFAULT_EASINESS_FACTOR = settings.DEFAULT_EASINESS_FACTOR
MIN_EASINESS_FACTOR = settings.MIN_EASINESS_FACTOR
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
