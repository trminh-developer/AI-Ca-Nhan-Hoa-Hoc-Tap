"""
Nyvora Adaptive Learning Platform - FastAPI Main Application (Python 3.14.x Clean Architecture).
"""

from contextlib import asynccontextmanager
import datetime
import platform
import sys

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    BackgroundScheduler = None

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.api.v1.router import api_v1_router
from app.core.config import ALLOWED_ORIGINS, settings
from app.core.exceptions import register_exception_handlers
from app.db.session import SessionLocal, create_tables
from app.models import (  # noqa: F401
    ChatHistory,
    ContentItem,
    Interaction,
    LearnerMastery,
    Question,
    RefreshToken,
    SpacedRepetition,
    Subject,
    SystemConfig,
    Topic,
    User,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời ứng dụng (Startup / Shutdown):
    1. Tạo & đồng bộ lược đồ cơ sở dữ liệu
    2. Đảm bảo tài khoản RBAC mặc định & ngân hàng 120 câu hỏi NCKH
    3. Khởi chạy Background Scheduler
    """
    print("🚀 Đang khởi tạo Nyvora Adaptive Learning Platform (Python 3.14.x)...")

    create_tables()
    print("✅ Đã tạo/kiểm tra tất cả bảng database")

    db = SessionLocal()
    try:
        from seed_data import ensure_default_accounts, seed_all

        ensure_default_accounts(db)
        topic_count = db.query(Topic).count()
        if topic_count < 12:
            print("📦 Đang đồng bộ bộ dữ liệu chuẩn NCKH (3 môn x 4 chủ đề x 10 câu hỏi)...")
            seed_all(db)
            print("✅ Đã đồng bộ dữ liệu mẫu NCKH thành công!")
        else:
            print(f"📊 Database đã có {topic_count} chủ đề chuẩn NCKH")
    finally:
        db.close()

    scheduler = None
    if BackgroundScheduler is not None:
        scheduler = BackgroundScheduler()

        def nightly_cleanup():
            print(f"[{datetime.datetime.now()}] 🧹 Đang chạy Cron Job: dọn dẹp hệ thống...")

        def weekly_report():
            print(f"[{datetime.datetime.now()}] 📊 Đang chạy Cron Job: Tổng hợp báo cáo tuần...")

        scheduler.add_job(nightly_cleanup, "cron", hour=2, minute=0)
        scheduler.add_job(weekly_report, "cron", day_of_week="sun", hour=23, minute=0)
        scheduler.start()

    yield

    print("👋 Đang tắt Nyvora Adaptive Learning Platform...")
    if scheduler is not None:
        scheduler.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "🎓 **Nyvora — Nền tảng Học tập Thích ứng Cá nhân hóa bằng AI (NCKH)**\n\n"
        "- 📊 **Dual Elo Rating System** ($O(1)$ Dynamic Latent Trait Estimation)\n"
        "- 🎯 **Zone of Proximal Development (ZPD)** ($0.60 \\le E_L \\le 0.75$)\n"
        "- 🧠 **SM-2 Spaced Repetition** (Chống đường cong quên lãng Ebbinghaus)\n"
        "- 📈 **Bloom's Revised Taxonomy** (6 cấp độ nhận thức có điều kiện tiên quyết)\n"
        "- 🤖 **Socratic AI Tutor** trên nền **Python 3.14.x** & `google-genai`"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Đăng ký Global Exception Handlers chuẩn hóa
register_exception_handlers(app)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount cả /api (tương thích ngược) và /api/v1 (kiến trúc chuẩn v1)
app.include_router(api_v1_router, prefix="/api")
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - Thông tin hệ thống API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Nền tảng học tập thích ứng sử dụng Dual Elo Rating, ZPD, SM-2 và Socratic AI",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "v1": "/api/v1",
            "content": "/api/subjects, /api/topics",
            "learning": "/api/learning",
            "spaced_review": "/api/spaced-review",
            "quiz": "/api/quiz",
            "chat": "/api/chat",
            "python_runtime": platform.python_version(),
        },
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "adaptive-learning-api",
        "python_version": platform.python_version(),
    }
