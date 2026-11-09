"""
API v1 Master Router - Hợp nhất toàn bộ các Endpoint của hệ thống Nyvora.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    chat,
    quiz,
    spaced_review,
    subjects,
    topics,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(subjects.router)
api_v1_router.include_router(topics.router)
api_v1_router.include_router(quiz.router)
api_v1_router.include_router(spaced_review.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(admin.router)
