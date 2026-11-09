"""
Chatbot Endpoints (Python 3.14.x) - Trợ giảng AI Socratic qua SDK `google-genai`.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.chat import ChatHistory
from app.models.user import User
from app.services.tutor_service import chatbot_service

router = APIRouter(prefix="/chat", tags=["Socratic AI Tutor (Python 3.14)"])


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class DemoHistoryTurn(BaseModel):
    role: str
    message: str


class DemoChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    learner_elo: float = Field(default=950.0, ge=100.0, le=3000.0)
    history: list[DemoHistoryTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    python_version: str
    engine: str


class ChatHistoryResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: str


@router.get("/runtime")
def get_chatbot_runtime():
    """Trả về thông tin môi trường chạy Python 3.14.x của dịch vụ Socratic AI Tutor."""
    return chatbot_service.get_runtime_info()


@router.post("/demo", response_model=ChatResponse)
def chat_demo(chat_request: DemoChatRequest):
    """
    Endpoint Chatbot Socratic công khai chạy trên Python 3.14.x cho trang chủ
    và khách chưa đăng nhập.
    """
    recent_turns = [
        {"role": t.role, "message": t.message}
        for t in chat_request.history[-10:]
    ]
    result = chatbot_service.generate_reply(
        user_message=chat_request.message,
        username="Khách trải nghiệm",
        overall_elo=chat_request.learner_elo,
        history=recent_turns,
    )
    return ChatResponse(
        reply=result.reply,
        python_version=result.python_version,
        engine=result.engine,
    )


@router.get("/history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy lịch sử hội thoại đã lưu của học viên hiện tại."""
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    return [
        ChatHistoryResponse(
            id=h.id,
            role=h.role,
            message=h.message,
            created_at=h.created_at.isoformat(),
        )
        for h in history
    ]


@router.post("/", response_model=ChatResponse)
def chat_with_bot(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Nhận tin nhắn của học viên đã đăng nhập, lưu DB và sinh phản hồi Socratic thích ứng
    theo điểm Elo trên nền tảng Python 3.14.x (Sliding Window 10 turns).
    """
    user_msg = chat_request.message.strip()

    user_history = ChatHistory(user_id=current_user.id, role="user", message=user_msg)
    db.add(user_history)
    db.commit()

    past_chats = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.user_id == current_user.id,
            ChatHistory.id != user_history.id,
        )
        .order_by(ChatHistory.created_at.desc())
        .limit(10)
        .all()
    )
    past_chats.reverse()

    history_payload = [
        {"role": h.role, "message": h.message}
        for h in past_chats
    ]

    result = chatbot_service.generate_reply(
        user_message=user_msg,
        username=current_user.username,
        overall_elo=current_user.overall_elo,
        history=history_payload,
    )

    bot_history = ChatHistory(user_id=current_user.id, role="model", message=result.reply)
    db.add(bot_history)
    db.commit()

    return ChatResponse(
        reply=result.reply,
        python_version=result.python_version,
        engine=result.engine,
    )
