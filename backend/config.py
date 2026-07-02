"""
Cấu hình ứng dụng - Quản lý các biến môi trường và cài đặt hệ thống.
Hỗ trợ SQL Server qua pymssql.
"""

import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình SQL Server (Đang gặp lỗi do SQL Server tắt TCP/IP)
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "AdaptiveLearningDB")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# TẠM THỜI CHUYỂN SANG SQLITE ĐỂ CHẠY ĐƯỢC LUÔN (Fix all)
# Vì pymssql bắt buộc cần TCP/IP nhưng SQL Server của bạn đang tắt.
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(base_dir, 'adaptive_learning.db')}"

# Cấu hình JWT Authentication
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "nckh-adaptive-learning-secret-key-change-in-production-2024"
)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Cấu hình Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # 24 giờ

# Cấu hình Elo Rating
INITIAL_ELO = 1500.0
K_FACTOR = 32  # Hệ số K cho thuật toán Elo

# Cấu hình CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
