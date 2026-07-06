"""
Main Application - Điểm khởi chạy ứng dụng FastAPI.

Bao gồm:
- Cấu hình CORS middleware
- Đăng ký tất cả routers
- Khởi tạo database và seed data khi startup
- Root endpoint trả về thông tin API
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from config import ALLOWED_ORIGINS
from database import create_tables, SessionLocal
from models import (  # noqa: F401 - Import để SQLAlchemy nhận diện tất cả models
    User, Subject, Topic, ContentItem, Question,
    Interaction, LearnerMastery, SpacedRepetition,
)
from routers import auth, content, learning, assessment, admin, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager - chạy khi app khởi động và tắt.
    
    Startup:
    1. Tạo tất cả bảng trong database
    2. Seed dữ liệu mẫu nếu database trống
    """
    # === STARTUP ===
    print("🚀 Đang khởi tạo Adaptive Learning Platform...")
    
    # Tạo bảng
    create_tables()
    print("✅ Đã tạo/kiểm tra tất cả bảng database")
    
    # Seed dữ liệu nếu trống
    db = SessionLocal()
    try:
        subject_count = db.query(Subject).count()
        if subject_count == 0:
            print("📦 Database trống - đang seed dữ liệu mẫu...")
            from seed_data import seed_all
            seed_all(db)
            print("✅ Đã seed dữ liệu mẫu thành công!")
        else:
            print(f"📊 Database đã có {subject_count} môn học - bỏ qua seed")
    finally:
        db.close()
    
    print("🎓 Adaptive Learning Platform sẵn sàng!")
    print("📖 Truy cập API docs tại: http://localhost:8000/docs")
    
    # Khởi tạo Scheduler (Cron jobs)
    scheduler = BackgroundScheduler()
    
    def nightly_cleanup():
        print(f"[{datetime.datetime.now()}] 🧹 Đang chạy Cron Job: dọn dẹp hệ thống...")
        # TODO: Implement real cleanup logic
    
    def weekly_report():
        print(f"[{datetime.datetime.now()}] 📊 Đang chạy Cron Job: Tổng hợp báo cáo tuần...")
        # TODO: Implement weekly report logic

    scheduler.add_job(nightly_cleanup, 'cron', hour=2, minute=0) # Chạy lúc 2:00 sáng mỗi ngày
    scheduler.add_job(weekly_report, 'cron', day_of_week='sun', hour=23, minute=0) # Chạy Chủ nhật lúc 23:00
    
    scheduler.start()
    print("⏳ Đã khởi động Hệ thống Background Scheduler")
    
    yield  # Ứng dụng đang chạy
    
    # === SHUTDOWN ===
    print("👋 Đang tắt Adaptive Learning Platform...")
    scheduler.shutdown()


# Tạo FastAPI app
app = FastAPI(
    title="Adaptive Learning Platform API",
    description=(
        "🎓 Nền tảng học tập thích ứng sử dụng AI\n\n"
        "**Tính năng chính:**\n"
        "- 📊 Elo Rating System để đánh giá trình độ học sinh\n"
        "- 🧠 SM-2 Spaced Repetition để tối ưu lịch ôn tập\n"
        "- 🎯 Zone of Proximal Development (ZPD) để đề xuất nội dung\n"
        "- 📈 Bloom's Taxonomy để phân loại mức độ tư duy\n\n"
        "**Nghiên cứu khoa học (NCKH)** - Ứng dụng AI trong cá nhân hóa học tập"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(learning.router)
app.include_router(assessment.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - Thông tin về API."""
    return {
        "name": "Adaptive Learning Platform API",
        "version": "1.0.0",
        "description": "Nền tảng học tập thích ứng sử dụng Elo Rating và SM-2",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "content": "/api/subjects, /api/topics",
            "learning": "/api/learning",
            "quiz": "/api/quiz",
        },
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "adaptive-learning-api"}
