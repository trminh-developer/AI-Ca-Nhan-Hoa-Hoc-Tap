import sys
import os

# Đảm bảo có thể import từ models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, create_tables
from models.content import Subject, Topic, Question

def seed_data():
    db = SessionLocal()
    
    # Tạo bảng nếu chưa có
    create_tables()

    subjects_data = [
        {"name": "Toán học", "icon": "📐", "desc": "Đại số, Giải tích, Hình học..."},
        {"name": "Vật lý", "icon": "⚡", "desc": "Cơ học, Điện từ học, Quang học..."},
        {"name": "Hóa học", "icon": "🧪", "desc": "Hóa vô cơ, Hóa hữu cơ..."},
        {"name": "Sinh học", "icon": "🧬", "desc": "Di truyền học, Tế bào, Sinh thái..."},
        {"name": "Ngữ văn", "icon": "📝", "desc": "Văn học Việt Nam, Văn học nước ngoài..."},
        {"name": "Tiếng Anh", "icon": "🌍", "desc": "Ngữ pháp, Từ vựng, Đọc hiểu..."},
        {"name": "Lịch sử", "icon": "🏛️", "desc": "Lịch sử thế giới, Lịch sử Việt Nam..."},
        {"name": "Địa lý", "icon": "🗺️", "desc": "Địa lý tự nhiên, Địa lý kinh tế xã hội..."},
        {"name": "Tin học", "icon": "💻", "desc": "Lập trình, Thuật toán, Cơ sở dữ liệu..."}
    ]

    print("Đang tạo các môn học...")
    added_subjects = []
    for s_data in subjects_data:
        existing = db.query(Subject).filter(Subject.name == s_data["name"]).first()
        if not existing:
            new_subject = Subject(name=s_data["name"], description=s_data["desc"], icon_emoji=s_data["icon"])
            db.add(new_subject)
            added_subjects.append(new_subject)
            
    db.commit()
    
    # Reload subjects
    all_subjects = db.query(Subject).all()
    subject_map = {s.name: s for s in all_subjects}
    
    print(f"Đã cập nhật {len(all_subjects)} môn học.")

    # Thêm một số Chủ đề mẫu cho Toán học
    math_subject = subject_map.get("Toán học")
    if math_subject:
        topics_data = [
            {"name": "Đại số 10: Mệnh đề và Tập hợp", "desc": "Các khái niệm cơ bản về logic và tập hợp.", "bloom": 1, "order": 1},
            {"name": "Đại số 10: Hàm số bậc nhất và bậc hai", "desc": "Đồ thị và tính chất của hàm số cơ bản.", "bloom": 2, "order": 2},
            {"name": "Đại số 11: Lượng giác", "desc": "Phương trình và công thức lượng giác.", "bloom": 3, "order": 1}
        ]
        for t_data in topics_data:
            ext_topic = db.query(Topic).filter(Topic.name == t_data["name"], Topic.subject_id == math_subject.id).first()
            if not ext_topic:
                new_topic = Topic(
                    subject_id=math_subject.id,
                    name=t_data["name"],
                    description=t_data["desc"],
                    bloom_level=t_data["bloom"],
                    order_index=t_data["order"]
                )
                db.add(new_topic)
        db.commit()
        print("Đã thêm các chủ đề mẫu cho Toán học.")
        
    db.close()
    print("Hoàn tất Build môn học!")

if __name__ == "__main__":
    seed_data()
