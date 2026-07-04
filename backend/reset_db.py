import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import engine, Base
from models.user import User
from models.content import Subject, Topic, ContentItem, Question
from seed_data import seed_all
from database import SessionLocal

print("⏳ Đang xóa toàn bộ bảng cũ trên Supabase...")
Base.metadata.drop_all(bind=engine)
print("✅ Đã xóa toàn bộ bảng cũ.")

print("⏳ Đang tạo lại các bảng mới (với Role và teacher_id)...")
Base.metadata.create_all(bind=engine)
print("✅ Đã tạo bảng thành công.")

print("⏳ Đang nạp dữ liệu mẫu (Seed Data)...")
db = SessionLocal()
try:
    seed_all(db)
    print("✅ Đã hoàn tất nạp dữ liệu mẫu!")
finally:
    db.close()
