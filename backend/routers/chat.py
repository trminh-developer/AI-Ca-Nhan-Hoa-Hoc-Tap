"""
Chatbot Router - Xử lý gửi/nhận tin nhắn với Trợ giảng Ảo qua Google Gemini API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import google.generativeai as genai

from database import get_db
from models.user import User
from models.chat import ChatHistory
from services.auth_service import get_current_user
from config import GEMINI_API_KEY

router = APIRouter(prefix="/api/chat", tags=["Chatbot"], dependencies=[Depends(get_current_user)])

# Cấu hình Gemini API nếu có key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ChatHistoryResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: str

@router.get("/history")
def get_chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy lịch sử chat của user"""
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    
    return [
        {
            "id": h.id,
            "role": h.role,
            "message": h.message,
            "created_at": h.created_at.isoformat()
        } for h in history
    ]


@router.post("/", response_model=ChatResponse)
def chat_with_bot(chat_request: ChatMessage, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Nhận tin nhắn của user, lưu DB, và trả về phản hồi từ AI.
    """
    user_msg = chat_request.message.strip()
    
    if not model:
        return ChatResponse(reply="⚠️ Tính năng AI chưa được kích hoạt. Vui lòng thêm API Key.")
    
    # Lưu câu hỏi của user vào DB
    user_history = ChatHistory(user_id=current_user.id, role='user', message=user_msg)
    db.add(user_history)
    db.commit()
    
    # Lấy 10 tin nhắn gần nhất làm context
    past_chats = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.desc()).limit(10).all()
    past_chats.reverse()
    
    context_str = "\n".join([f"{'Học viên' if h.role == 'user' else 'AI'}: {h.message}" for h in past_chats[:-1]])

    # Chuẩn bị Prompt với bối cảnh hệ thống
    system_prompt = (
        f"Bạn là Trợ giảng Ảo AI của hệ thống học tập LearnAI. Bạn đang nói chuyện với học viên tên {current_user.username}. "
        f"Điểm năng lực Elo của học viên này là {int(current_user.overall_elo)}. "
        f"Nếu điểm Elo dưới 1200 (Novice), giải thích thật đơn giản. "
        f"Nếu điểm Elo từ 1200-1500 (Intermediate), giải thích bình thường. "
        f"Nếu điểm Elo trên 1500 (Advanced/Master), giải thích chuyên sâu. "
        f"Chỉ trả lời câu hỏi liên quan học tập. Nếu học viên hỏi linh tinh, hãy khéo léo đưa về chủ đề học.\n\n"
        f"Lịch sử trò chuyện gần đây:\n{context_str}\n\n"
        f"Học viên: {user_msg}\nAI:"
    )

    try:
        response = model.generate_content(system_prompt)
        reply = response.text
    except Exception as e:
        reply = "Đã có lỗi xảy ra khi kết nối với AI. Lỗi chi tiết: " + str(e)
        
    # Lưu câu trả lời của AI vào DB
    bot_history = ChatHistory(user_id=current_user.id, role='model', message=reply)
    db.add(bot_history)
    db.commit()

    return ChatResponse(reply=reply)
