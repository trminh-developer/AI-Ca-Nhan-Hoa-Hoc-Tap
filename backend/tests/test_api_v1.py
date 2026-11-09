"""
Integration Tests cho API v1:
- Access Token + Refresh Token Rotation & Logout
- Global Exception Handler chuẩn hóa
- Socratic AI Tutor 3-tier theo Elo trên Python 3.14.x
- Analytics Progress (Elo History & Bloom Radar)
"""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal, create_tables
from app.main import app
from seed_data import ensure_default_accounts

create_tables()
_db = SessionLocal()
try:
    ensure_default_accounts(_db)
finally:
    _db.close()

client = TestClient(app)


def test_v1_health_and_exception_format():
    """Kiểm tra /health và định dạng lỗi chuẩn hóa của Global Exception Handler."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    not_found = client.get("/api/v1/subjects/999999/topics")
    assert not_found.status_code == 404
    body = not_found.json()
    assert body["status"] == "error"
    assert body["code"] in ("NOT_FOUND", "HTTP_404")
    assert "detail" in body
    assert "timestamp" in body


def test_v1_jwt_refresh_and_logout_flow():
    """Kiểm tra luồng đăng nhập nhận Access + Refresh Token, làm mới phiên và thu hồi token."""
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "student", "password": "student123"},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["role"] == "student"

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_resp.status_code == 200
    rotated = refresh_resp.json()
    assert rotated["access_token"]
    assert rotated["refresh_token"] != tokens["refresh_token"]

    logout_resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": rotated["refresh_token"]},
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["revoked"] is True


def test_v1_socratic_tutor_tiers():
    """Kiểm tra Socratic AI Tutor thích ứng theo 3 dải Elo (<1200, 1200-1800, >1800)."""
    from app.services.tutor_service import chatbot_service

    saved_client = chatbot_service._client
    chatbot_service._client = None
    try:
        for elo in (950.0, 1500.0, 1950.0):
            resp = client.post(
                "/api/v1/chat/demo",
                json={"message": "O(log n) là gì?", "learner_elo": elo},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["reply"]) > 20
            assert data["python_version"].startswith("3.")
    finally:
        chatbot_service._client = saved_client
