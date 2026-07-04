"""
Test Suite - Kiểm thử toàn bộ API cho Adaptive Learning Platform.

Bao gồm:
- Auth API: Register, Login, GetMe, UpdateMe
- Content API: Subjects, Topics, Questions
- Learning API: Submit Answer, Progress, Mastery
- Quiz API: Start, Submit
- Admin API: Stats, Users, Role
- Chat API: Send message
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models.content import Subject, Topic, Question
from models.user import User
from services.auth_service import hash_password

# ═══════════════ TEST DATABASE SETUP ═══════════════

# Sử dụng SQLite in-memory cho test (không ảnh hưởng DB chính)
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, raise_server_exceptions=False)


def setup_db():
    """Tạo tất cả bảng và seed dữ liệu test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()

    # Tạo admin
    admin = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
        overall_elo=1500.0,
    )
    db.add(admin)

    # Tạo môn học
    subject = Subject(name="Python Test", description="Test subject", icon_emoji="🐍")
    db.add(subject)
    db.flush()

    # Tạo chủ đề
    topic = Topic(
        subject_id=subject.id,
        name="Variables",
        description="Test topic",
        bloom_level=1,
        order_index=1,
    )
    db.add(topic)
    db.flush()

    # Tạo câu hỏi
    for i in range(5):
        q = Question(
            topic_id=topic.id,
            question_text=f"Test question {i+1}?",
            option_a="A", option_b="B", option_c="C", option_d="D",
            correct_answer="a",
            explanation=f"Explanation {i+1}",
            difficulty_elo=1000 + i * 100,
            bloom_level=1,
        )
        db.add(q)

    db.commit()
    db.close()


# ═══════════════ HELPER ═══════════════

def get_admin_token():
    """Đăng nhập admin và trả về token."""
    resp = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    return resp.json()["access_token"]


def get_user_token(username="testuser", password="test123456"):
    """Đăng nhập user và trả về token."""
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ═══════════════ TEST RUNNER ═══════════════

passed = 0
failed = 0
errors = []


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        errors.append(f"{name}: {detail}")
        print(f"  ❌ {name} — {detail}")


# ═══════════════ TESTS ═══════════════

def test_root_and_health():
    print("\n📋 [1] Root & Health Check")
    
    resp = client.get("/")
    test("GET / returns 200", resp.status_code == 200)
    test("Root has API name", "Adaptive" in resp.json().get("name", ""))

    resp = client.get("/health")
    test("GET /health returns 200", resp.status_code == 200)
    test("Health status is healthy", resp.json().get("status") == "healthy")


def test_auth_register():
    print("\n📋 [2] Auth - Register")

    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "test123456",
    })
    test("Register returns 201", resp.status_code == 201, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 201:
        data = resp.json()
        test("Register returns username", data.get("username") == "testuser")
        test("Register returns email", data.get("email") == "test@test.com")
        test("Register returns elo 1500", data.get("overall_elo") == 1500.0)
        test("Register returns is_admin=false", data.get("is_admin") == False)

    # Duplicate username
    resp2 = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "other@test.com",
        "password": "test123456",
    })
    test("Duplicate username returns 400", resp2.status_code == 400)

    # Duplicate email
    resp3 = client.post("/api/auth/register", json={
        "username": "otheruser",
        "email": "test@test.com",
        "password": "test123456",
    })
    test("Duplicate email returns 400", resp3.status_code == 400)

    # Invalid email
    resp4 = client.post("/api/auth/register", json={
        "username": "baduser",
        "email": "not-an-email",
        "password": "test123456",
    })
    test("Invalid email returns 422", resp4.status_code == 422)

    # Short password
    resp5 = client.post("/api/auth/register", json={
        "username": "shortpw",
        "email": "short@test.com",
        "password": "123",
    })
    test("Short password returns 422", resp5.status_code == 422)


def test_auth_login():
    print("\n📋 [3] Auth - Login")

    resp = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "test123456",
    })
    test("Login returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        test("Login returns access_token", "access_token" in data)
        test("Login returns bearer type", data.get("token_type") == "bearer")

    # Wrong password
    resp2 = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword",
    })
    test("Wrong password returns 401", resp2.status_code == 401)

    # Non-existent user
    resp3 = client.post("/api/auth/login", data={
        "username": "nobody",
        "password": "test123456",
    })
    test("Non-existent user returns 401", resp3.status_code == 401)


def test_auth_me():
    print("\n📋 [4] Auth - Get/Update Me")

    token = get_user_token()

    # GET /me
    resp = client.get("/api/auth/me", headers=auth_header(token))
    test("GET /me returns 200", resp.status_code == 200)
    if resp.status_code == 200:
        data = resp.json()
        test("GET /me returns correct username", data.get("username") == "testuser")
        test("GET /me returns correct email", data.get("email") == "test@test.com")

    # Without token
    resp2 = client.get("/api/auth/me")
    test("GET /me without token returns 401", resp2.status_code == 401)

    # PUT /me - Update email
    resp3 = client.put("/api/auth/me", headers=auth_header(token), json={
        "email": "updated@test.com",
    })
    test("PUT /me update email returns 200", resp3.status_code == 200)
    if resp3.status_code == 200:
        test("Email was updated", resp3.json().get("email") == "updated@test.com")

    # PUT /me - Update password
    resp4 = client.put("/api/auth/me", headers=auth_header(token), json={
        "password": "newpassword123",
    })
    test("PUT /me update password returns 200", resp4.status_code == 200)

    # Login with new password
    resp5 = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "newpassword123",
    })
    test("Login with new password works", resp5.status_code == 200)


def test_content_api():
    print("\n📋 [5] Content - Subjects, Topics, Questions")

    # Subjects (no auth needed)
    resp = client.get("/api/subjects")
    test("GET /subjects returns 200", resp.status_code == 200)
    if resp.status_code == 200:
        data = resp.json()
        test("Subjects is a list", isinstance(data, list))
        test("At least 1 subject exists", len(data) >= 1)
        if len(data) > 0:
            test("Subject has name field", "name" in data[0])
            subject_id = data[0]["id"]

            # Topics
            resp2 = client.get(f"/api/subjects/{subject_id}/topics")
            test("GET /subjects/{id}/topics returns 200", resp2.status_code == 200)
            topics = resp2.json()
            test("Topics is a list", isinstance(topics, list))
            if len(topics) > 0:
                topic_id = topics[0]["id"]
                test("Topic has name field", "name" in topics[0])

                # Questions (requires auth)
                token = get_user_token("testuser", "newpassword123")
                resp3 = client.get(f"/api/topics/{topic_id}/questions", headers=auth_header(token))
                test("GET /topics/{id}/questions returns 200", resp3.status_code == 200)
                questions = resp3.json()
                test("Questions is a list", isinstance(questions, list))
                if len(questions) > 0:
                    q = questions[0]
                    test("Question has question_text", "question_text" in q)
                    test("Question has options", "option_a" in q and "option_b" in q)
                    test("Question does NOT have correct_answer (public)", "correct_answer" not in q)

    # Non-existent subject
    resp4 = client.get("/api/subjects/99999/topics")
    test("Non-existent subject returns 404", resp4.status_code == 404)

    # Questions without auth
    resp5 = client.get("/api/topics/1/questions")
    test("Questions without auth returns 401", resp5.status_code == 401)


def test_learning_api():
    print("\n📋 [6] Learning - Answer, Progress, Mastery")

    token = get_user_token("testuser", "newpassword123")
    headers = auth_header(token)

    # Get a question first
    db = TestSessionLocal()
    question = db.query(Question).first()
    db.close()

    if not question:
        test("Question exists for testing", False, "No question in DB")
        return

    # Submit correct answer
    resp = client.post("/api/learning/answer", headers=headers, json={
        "question_id": question.id,
        "selected_answer": "a",
        "time_spent_ms": 5000,
    })
    test("POST /learning/answer returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        test("Answer result has is_correct", "is_correct" in data)
        test("Correct answer is True", data.get("is_correct") == True)
        test("Answer has elo_change", "elo_change" in data)
        test("Answer has new_elo", "new_elo" in data)
        test("Answer has explanation", "explanation" in data)

    # Submit wrong answer
    resp2 = client.post("/api/learning/answer", headers=headers, json={
        "question_id": question.id,
        "selected_answer": "b",
        "time_spent_ms": 3000,
    })
    test("Wrong answer returns 200", resp2.status_code == 200)
    if resp2.status_code == 200:
        test("Wrong answer is_correct=False", resp2.json().get("is_correct") == False)

    # Non-existent question
    resp3 = client.post("/api/learning/answer", headers=headers, json={
        "question_id": 99999,
        "selected_answer": "a",
        "time_spent_ms": 1000,
    })
    test("Non-existent question returns 404", resp3.status_code == 404)

    # Progress
    resp4 = client.get("/api/learning/progress", headers=headers)
    test("GET /learning/progress returns 200", resp4.status_code == 200)
    if resp4.status_code == 200:
        data = resp4.json()
        test("Progress has overall_elo", "overall_elo" in data)
        test("Progress has total_questions_answered", data.get("total_questions_answered", 0) >= 2)
        test("Progress has accuracy_rate", "accuracy_rate" in data)
        test("Progress has topics_mastery list", isinstance(data.get("topics_mastery"), list))

    # Mastery
    resp5 = client.get("/api/learning/mastery", headers=headers)
    test("GET /learning/mastery returns 200", resp5.status_code == 200)

    # Review queue
    resp6 = client.get("/api/learning/review-queue", headers=headers)
    test("GET /learning/review-queue returns 200", resp6.status_code == 200)

    # Next question
    resp7 = client.get("/api/learning/next-question", headers=headers)
    test("GET /learning/next-question returns 200", resp7.status_code == 200)


def test_quiz_api():
    print("\n📋 [7] Quiz - Start, Submit")

    token = get_user_token("testuser", "newpassword123")
    headers = auth_header(token)

    db = TestSessionLocal()
    topic = db.query(Topic).first()
    db.close()

    if not topic:
        test("Topic exists for testing", False, "No topic in DB")
        return

    # Start quiz
    resp = client.post("/api/quiz/start", headers=headers, json={
        "topic_id": topic.id,
        "num_questions": 3,
    })
    test("POST /quiz/start returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        questions = resp.json()
        test("Quiz returns a list", isinstance(questions, list))
        test("Quiz returns <= 3 questions", len(questions) <= 3)
        if len(questions) > 0:
            test("Quiz question has id", "id" in questions[0])
            test("Quiz question has options", "option_a" in questions[0])

            # Submit quiz
            answers = [
                {"question_id": q["id"], "selected_answer": "a", "time_spent_ms": 3000}
                for q in questions
            ]
            resp2 = client.post("/api/quiz/submit", headers=headers, json={"answers": answers})
            test("POST /quiz/submit returns 200", resp2.status_code == 200, f"Got {resp2.status_code}: {resp2.text}")
            if resp2.status_code == 200:
                result = resp2.json()
                test("Quiz result has total_questions", "total_questions" in result)
                test("Quiz result has correct_count", "correct_count" in result)
                test("Quiz result has accuracy", "accuracy" in result)
                test("Quiz result has new_elo", "new_elo" in result)

    # Non-existent topic
    resp3 = client.post("/api/quiz/start", headers=headers, json={
        "topic_id": 99999,
        "num_questions": 5,
    })
    test("Non-existent topic returns 404", resp3.status_code == 404)

    # Empty answers
    resp4 = client.post("/api/quiz/submit", headers=headers, json={"answers": []})
    test("Empty answers returns 400", resp4.status_code == 400)


def test_admin_api():
    print("\n📋 [8] Admin - Stats, Users, Role")

    admin_token = get_admin_token()
    user_token = get_user_token("testuser", "newpassword123")

    # Stats - Admin
    resp = client.get("/api/admin/stats", headers=auth_header(admin_token))
    test("GET /admin/stats (admin) returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        test("Stats has total_users", data.get("total_users", 0) >= 1)
        test("Stats has total_subjects", data.get("total_subjects", 0) >= 1)

    # Stats - Non-admin
    resp2 = client.get("/api/admin/stats", headers=auth_header(user_token))
    test("GET /admin/stats (non-admin) returns 403", resp2.status_code == 403)

    # Users list
    resp3 = client.get("/api/admin/users", headers=auth_header(admin_token))
    test("GET /admin/users returns 200", resp3.status_code == 200)
    if resp3.status_code == 200:
        users = resp3.json()
        test("Users is a list", isinstance(users, list))
        test("Users has at least 2 (admin + testuser)", len(users) >= 2)

    # Update role
    db = TestSessionLocal()
    testuser = db.query(User).filter(User.username == "testuser").first()
    db.close()

    if testuser:
        resp4 = client.put(f"/api/admin/users/{testuser.id}/role",
                           headers=auth_header(admin_token),
                           json={"is_admin": True})
        test("PUT /admin/users/{id}/role returns 200", resp4.status_code == 200)
        if resp4.status_code == 200:
            test("User is now admin", resp4.json().get("is_admin") == True)

            # Revert
            client.put(f"/api/admin/users/{testuser.id}/role",
                       headers=auth_header(admin_token),
                       json={"is_admin": False})

    # Without auth
    resp5 = client.get("/api/admin/stats")
    test("Admin without auth returns 401", resp5.status_code == 401)


def test_chat_api():
    print("\n📋 [9] Chat API")

    token = get_user_token("testuser", "newpassword123")

    resp = client.post("/api/chat/", headers=auth_header(token), json={
        "message": "Hello",
    })
    test("POST /chat/ returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    if resp.status_code == 200:
        test("Chat has reply field", "reply" in resp.json())

    # Without auth
    resp2 = client.post("/api/chat/", json={"message": "Hello"})
    test("Chat without auth returns 401", resp2.status_code == 401)


# ═══════════════ MAIN ═══════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ADAPTIVE LEARNING PLATFORM - FULL API TEST SUITE")
    print("=" * 60)

    setup_db()

    test_root_and_health()
    test_auth_register()
    test_auth_login()
    test_auth_me()
    test_content_api()
    test_learning_api()
    test_quiz_api()
    test_admin_api()
    test_chat_api()

    print("\n" + "=" * 60)
    print(f"📊 KẾT QUẢ: {passed} passed / {failed} failed / {passed + failed} total")
    print("=" * 60)

    if errors:
        print("\n❌ CÁC LỖI:")
        for e in errors:
            print(f"  • {e}")

    print()
    sys.exit(1 if failed > 0 else 0)
