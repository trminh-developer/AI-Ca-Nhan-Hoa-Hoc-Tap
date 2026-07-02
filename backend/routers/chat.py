"""
Chatbot Router - Xử lý gửi/nhận tin nhắn với Trợ giảng Ảo qua Google Gemini API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import google.generativeai as genai

from database import get_db
from models.user import User
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


@router.post("/", response_model=ChatResponse)
def chat_with_bot(chat_request: ChatMessage, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Nhận tin nhắn của user và trả về phản hồi từ Google Gemini AI.
    """
    user_msg = chat_request.message.strip()
    
    if not model:
        return ChatResponse(reply="⚠️ Tính năng AI chưa được kích hoạt. Vui lòng lấy API Key tại Google AI Studio và thêm vào file .env mục GEMINI_API_KEY để AI có thể trả lời câu hỏi của bạn nhé!")
    
    # Chuẩn bị Prompt với bối cảnh hệ thống
    system_prompt = (
        f"Bạn là Trợ giảng Ảo AI của hệ thống học tập LearnAI. Bạn đang nói chuyện với học viên tên {current_user.username}. "
        f"Điểm năng lực Elo của học viên này là {int(current_user.overall_elo)}. "
        f"Nếu điểm Elo dưới 1200 (Novice), hãy giải thích thật đơn giản và dễ hiểu. "
        f"Nếu điểm Elo từ 1200-1500 (Intermediate), giải thích bình thường. "
        f"Nếu điểm Elo trên 1500 (Advanced/Master), hãy giải thích chuyên sâu và ngắn gọn. "
        f"Chỉ trả lời các câu hỏi liên quan đến học tập, IT, lập trình. Nếu học viên hỏi linh tinh, hãy khéo léo đưa họ về chủ đề học. "
        f"Câu hỏi của học viên: {user_msg}"
    )

    try:
        response = model.generate_content(system_prompt)
        reply = response.text
    except Exception as e:
        reply = "Đã có lỗi xảy ra khi kết nối với AI. Vui lòng thử lại sau! Lỗi chi tiết: " + str(e)
        
    return ChatResponse(reply=reply)
