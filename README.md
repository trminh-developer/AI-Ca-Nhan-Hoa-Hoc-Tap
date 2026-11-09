# 🧠 Nyvora — Nền tảng Học tập Thích ứng Cá nhân hóa bằng AI (NCKH)

![Python 3.14](https://img.shields.io/badge/Python-3.14.0-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Clean_Architecture-009688?logo=fastapi&logoColor=white)
![Next.js 16](https://img.shields.io/badge/Next.js-16.2_(React_19)-000000?logo=next.js&logoColor=white)
![Google GenAI](https://img.shields.io/badge/AI_SDK-google--genai-4285F4?logo=google&logoColor=white)
![KaTeX](https://img.shields.io/badge/Math-KaTeX_LaTeX-6366F1)

**Nyvora** là hệ sinh thái học tập thích ứng chu trình khép kín (*Closed-Loop Adaptive Learning Ecosystem*) được nghiên cứu và phát triển nhằm giải quyết bài toán giáo dục đồng loạt (*One-size-fits-all*): giúp học viên khá/giỏi tránh cảm giác nhàm chán và bảo vệ học viên trung bình/yếu khỏi tình trạng quá tải nhận thức (*Cognitive Overload*).

---

## 🔬 1. Cơ sở Khoa học & Mô hình Toán học Cốt lõi

### A. Hệ thống Dual Elo Rating (Biến thể Logistic IRT thời gian thực $O(1)$)
Xác suất kỳ vọng học viên $L$ trả lời đúng câu hỏi $I$:

$$E_L = \frac{1}{1 + 10^{\frac{R_I - R_L}{400}}}$$

Sau mỗi tương tác với điểm thực tế $S \in \{1.0, 0.5, 0.0\}$, điểm năng lực học viên $R_L$ và độ khó câu hỏi $R_I$ được hiệu chuẩn đồng thời:

$$R_L^{(new)} = R_L^{(old)} + K_L \cdot (S - E_L), \qquad R_I^{(new)} = R_I^{(old)} + K_I \cdot (E_L - S)$$

Trong đó hệ số nhạy $K_L$ co giãn động theo số lượt tương tác ($K_L = 32$ cho tài khoản mới để hội tụ nhanh, giảm dần về $K_L = 16$ khi ổn định).

### B. Vùng Phát triển Gần nhất (Zone of Proximal Development — ZPD)
Dựa trên lý thuyết của **Lev Vygotsky** và trạng thái **Flow (Csikszentmihalyi)**, hệ thống ưu tiên lựa chọn câu hỏi có xác suất thành công kỳ vọng nằm trong khoảng vàng:

$$0.60 \le E_L \le 0.75 \iff R_L - 85 \le R_I \le R_L + 170$$

Loại bỏ các câu hỏi quá dễ ($E_L > 0.85$) hoặc quá khó ($E_L < 0.40$).

### C. Lặp lại Ngắt quãng SuperMemo-2 (SM-2 Spaced Repetition)
Chống lại đường cong quên lãng **Hermann Ebbinghaus** dựa trên chất lượng ghi nhớ $q \in [0, 5]$ (tính từ tính đúng/sai, thời gian phản hồi $t$ (ms) và số lần mở gợi ý Socratic):

$$EF^{(new)} = \max\left(1.3, \; EF^{(old)} + \left(0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02)\right)\right)$$

Chu kỳ ôn tập $I(n)$ (ngày): $I(1) = 1, \; I(2) = 6, \; I(n) = \text{round}(I(n-1) \times EF)$ với $n \ge 3$. Nếu $q < 3$, chu kỳ tự động đặt lại $I = 1, \text{Repetitions} = 0$.

### D. Thang đo Nhận thức Bloom (6 Cấp độ Tiên quyết)
Ngân hàng câu hỏi được chuẩn hóa theo 6 bậc tư duy: **Remember (1) $\to$ Understand (2) $\to$ Apply (3) $\to$ Analyze (4) $\to$ Evaluate (5) $\to$ Create (6)**. Học viên chỉ được mở khóa câu hỏi ở bậc $k$ khi đạt $\text{Mastery Score} \ge 0.70$ ở bậc $k-1$.

### E. Trợ giảng AI Socratic trên nền Python 3.14.x (`google-genai`)
Sử dụng phương pháp vấn đáp **Socratic Scaffolding** cá nhân hóa theo 3 dải Elo:
- **Elo $< 1200$ (Cơ bản)**: Giải thích trực quan bằng ẩn dụ đời sống, chia nhỏ từng bước.
- **Elo $1200 - 1800$ (Trung cấp)**: Đi thẳng vào bản chất, đặt câu hỏi phản biện dẫn dắt.
- **Elo $> 1800$ (Chuyên sâu)**: Thảo luận độ phức tạp thuật toán Big-O, định lý toán học và tối ưu kiến trúc.

---

## 🏗️ 2. Kiến trúc Hệ thống (Clean Architecture)

```text
NCKH/
├── backend/                        # Python 3.14.x + FastAPI + SQLAlchemy 2.0 + Alembic
│   ├── alembic/                    # Quản lý tiến hóa lược đồ Database (Migrations)
│   ├── app/
│   │   ├── api/v1/endpoints/       # RESTful API v1: auth, subjects, topics, quiz, spaced_review, chat, admin
│   │   ├── core/                   # Settings (Pydantic v2), Security (JWT Access + Refresh Rotation), Exceptions
│   │   ├── db/                     # Declarative Base, Session & Auto DNS-Fallback (Supabase -> SQLite)
│   │   ├── models/                 # User, RefreshToken, SystemConfig, Subject, Topic, Question, Interaction, SM2, Chat
│   │   ├── schemas/                # Pydantic v2 Request/Response Schemas
│   │   ├── services/               # elo_service, sm2_service, zpd_service, tutor_service, analytics_service
│   │   └── main.py                 # FastAPI Application Entrypoint
│   ├── tests/                      # Pytest Unit & Integration Suite (Elo, SM-2, ZPD, API v1)
│   ├── seed_data.py                # Ngân hàng 120 câu hỏi NCKH (3 môn x 4 chủ đề x 10 câu có LaTeX & Code)
│   └── test_api.py                 # Bộ kiểm thử tích hợp 92 kịch bản End-to-End
└── frontend/                       # Next.js 16 (App Router) + React 19 + TypeScript + KaTeX + Recharts
    └── src/
        ├── app/                    # Landing, Login, Register, Dashboard (Recharts + SM-2), Quiz Room, Admin Hub
        ├── components/             # MathText (KaTeX + Code Copy), Chatbot Socratic, AuthGuard, RoleGuard
        ├── context/                # AuthContext (Silent Refresh Token Rotation & RBAC state)
        └── lib/                    # API Client chuẩn hóa & tiện ích Elo/Bloom
```

---

## 🚀 3. Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống
- **Backend**: Python `3.14.x`
- **Frontend**: Node.js `>= 20.x`

### Bước 1: Khởi chạy Backend (Cổng `8000`)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Chạy kiểm thử tự động (Unit Tests + Integration Tests)
pytest tests -v
python test_api.py

# Khởi động máy chủ FastAPI (Tự động khởi tạo bảng & seed 120 câu hỏi NCKH)
uvicorn app.main:app --reload --port 8000
```
- Tài liệu Swagger UI: `http://localhost:8000/docs`

### Bước 2: Khởi chạy Frontend (Cổng `3000`)
```bash
cd frontend
npm install
npm run dev
```
- Truy cập giao diện web tại: `http://localhost:3000`

---

## 🔐 4. Tài khoản Mẫu Phân quyền (RBAC)

| Vai trò | Tên đăng nhập | Mật khẩu | Quyền hạn chính |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` hoặc `trminhdev` | `admin123` / `123456` | Toàn quyền quản trị người dùng, gán giảng viên, CRUD câu hỏi LaTeX, cấu hình $K$-factor & ZPD, Seed DB |
| **Giảng viên (Teacher)** | `teacher` | `teacher123` | Xem học viên được phân công, tạo/sửa/xóa ngân hàng câu hỏi của mình |
| **Học viên (Student)** | `student` | `student123` | Làm bài thích ứng ZPD, ôn tập Flashcard SM-2, xem biểu đồ Elo & Bloom Radar, chat Socratic AI |
