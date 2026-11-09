"""
Root Config Compatibility Layer - Re-exports from `app.core.config`.
"""

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    ALLOWED_ORIGINS,
    DATABASE_URL,
    DEFAULT_EASINESS_FACTOR,
    DEFAULT_ELO,
    GEMINI_API_KEY,
    GEMINI_FALLBACK_MODELS,
    GEMINI_MODEL,
    K_FACTOR_ITEM,
    K_FACTOR_LEARNER,
    MIN_EASINESS_FACTOR,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    Settings,
    settings,
)

__all__ = [
    "Settings",
    "settings",
    "DATABASE_URL",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",
    "DEFAULT_ELO",
    "K_FACTOR_LEARNER",
    "K_FACTOR_ITEM",
    "DEFAULT_EASINESS_FACTOR",
    "MIN_EASINESS_FACTOR",
    "ALLOWED_ORIGINS",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GEMINI_FALLBACK_MODELS",
]
