"""
Root Entrypoint - Re-exports `app` from `app.main` for backward compatibility (`uvicorn main:app`).
"""

from app.main import app, health_check, lifespan, root

__all__ = ["app", "lifespan", "root", "health_check"]
