"""
Chatbot Service (Python 3.14.x) - Trợ giảng AI Thích ứng theo Elo cho nền tảng Nyvora.

Sử dụng SDK chính thức `google-genai` tương thích chuẩn với Python 3.14.x,
kèm bộ phản hồi sư phạm thích ứng dự phòng (Adaptive Fallback Tutor) khi chưa cấu hình
hoặc hết hạn khóa Gemini API.
"""

from dataclasses import dataclass
import platform
import sys

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

type ConversationTurn = dict[str, str]


@dataclass(slots=True)
class ChatbotReplyResult:
    """Kết quả trả lời từ hệ thống Trợ giảng AI Python 3.14.x."""
    reply: str
    engine: str
    python_version: str


class NyvoraChatbotService:
    """
    Dịch vụ Trợ giảng Ảo chạy trên Python 3.14.x.

    - Tự động nhận diện khóa Google AI Studio (`AIza...`) hoặc Vertex AI Express (`AQ....`)
    - Điều chỉnh độ sâu sư phạm theo mức năng lực Elo của người học
    - Hỗ trợ cả hội thoại có lưu lịch sử (Authenticated) và dùng thử trực tiếp (Demo/Guest)
    """

    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL) -> None:
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name or "gemini-2.5-flash"
        self.python_version = platform.python_version()
        self._client: genai.Client | None = None

        if self.api_key:
            try:
                if self.api_key.startswith("AQ."):
                    self._client = genai.Client(vertexai=True, api_key=self.api_key)
                else:
                    self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def is_ai_configured(self) -> bool:
        """Kiểm tra client Gemini SDK đã được khởi tạo hay chưa."""
        return self._client is not None

    def get_runtime_info(self) -> dict[str, str | bool]:
        """Trả về thông tin môi trường chạy Python 3.14.x của Chatbot."""
        return {
            "service": "nyvora-chatbot",
            "language": "Python",
            "python_version": self.python_version,
            "python_series": f"{sys.version_info.major}.{sys.version_info.minor}",
            "sdk": "google-genai",
            "model": self.model_name,
            "ai_configured": self.is_ai_configured,
        }

    @staticmethod
    def _resolve_elo_tier(elo: float) -> tuple[str, str]:
        """Phân tầng chiến lược sư phạm theo điểm Elo của người học."""
        if elo < 1200:
            return (
                "Novice (Nhập môn)",
                "Giải thích thật trực quan, ngắn gọn, dùng ví dụ đời thường dễ hiểu, tránh thuật ngữ quá hàn lâm.",
            )
        if elo <= 1500:
            return (
                "Intermediate (Trung cấp)",
                "Giải thích cân bằng giữa lý thuyết và thực hành, kèm ví dụ minh họa và câu hỏi gợi mở tư duy.",
            )
        return (
            "Advanced/Master (Nâng cao)",
            "Giải thích chuyên sâu về bản chất thuật toán, độ phức tạp, edge cases và tối ưu hóa hệ thống.",
        )

    def build_system_instruction(self, username: str, overall_elo: float) -> str:
        """Xây dựng System Instruction cá nhân hóa theo người học."""
        tier_name, pedagogy_guide = self._resolve_elo_tier(overall_elo)
        return (
            f"Bạn là Trợ giảng Ảo AI của nền tảng học tập thích ứng Nyvora (vận hành trên Python {self.python_version}). "
            f"Bạn đang hỗ trợ người học '{username}' có điểm năng lực Elo hiện tại là {int(overall_elo)} — cấp độ {tier_name}. "
            f"Nguyên tắc sư phạm: {pedagogy_guide} "
            "Khi hướng dẫn lập trình Python, hãy ưu tiên chuẩn ngôn ngữ Python 3.14.x hiện đại. "
            "Chỉ tập trung trả lời các chủ đề học tập, lập trình, toán học, khoa học máy tính, ngoại ngữ và phương pháp ôn tập. "
            "Nếu người học hỏi ngoài lề, hãy lịch sự khéo léo dẫn dắt quay lại bài học."
        )

    def generate_reply(
        self,
        user_message: str,
        username: str = "Học viên",
        overall_elo: float = 1200.0,
        history: list[ConversationTurn] | None = None,
    ) -> ChatbotReplyResult:
        """
        Sinh phản hồi cho tin nhắn của học viên qua SDK `google-genai` trên Python 3.14.x.
        Tự động chuyển sang bộ phản hồi sư phạm thích ứng nội bộ nếu khóa API chưa hợp lệ.
        """
        cleaned_msg = user_message.strip()
        if not cleaned_msg:
            return ChatbotReplyResult(
                reply="Bạn hãy nhập câu hỏi hoặc chủ đề cần giải thích nhé!",
                engine="python-3.14-validator",
                python_version=self.python_version,
            )

        if self._client is not None:
            contents: list[types.Content] = []
            for turn in history or []:
                turn_text = (turn.get("message") or "").strip()
                if not turn_text:
                    continue
                role = "user" if turn.get("role") == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=turn_text)],
                    )
                )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=cleaned_msg)],
                )
            )

            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self.build_system_instruction(username, overall_elo),
                        temperature=0.7,
                    ),
                )
                if response and response.text:
                    return ChatbotReplyResult(
                        reply=response.text.strip(),
                        engine=f"google-genai/{self.model_name}",
                        python_version=self.python_version,
                    )
            except Exception:
                # Chuyển mượt sang Adaptive Fallback Tutor của Python 3.14 để không làm gián đoạn việc học
                pass

        fallback_reply = self._generate_adaptive_fallback_reply(
            message=cleaned_msg,
            username=username,
            overall_elo=overall_elo,
        )
        return ChatbotReplyResult(
            reply=fallback_reply,
            engine="python-3.14-adaptive-tutor",
            python_version=self.python_version,
        )

    def _generate_adaptive_fallback_reply(
        self,
        message: str,
        username: str,
        overall_elo: float,
    ) -> str:
        """
        Bộ phản hồi sư phạm thích ứng chạy thuần Python 3.14.x (dùng structural match/case)
        khi môi trường chưa cấu hình hoặc hết hạn GEMINI_API_KEY.
        """
        lowered = message.lower()
        tier_name, _ = self._resolve_elo_tier(overall_elo)
        elo_int = int(overall_elo)

        topic_key = "general"
        if "log" in lowered or "binary search" in lowered or "nhị phân" in lowered:
            topic_key = "ologn"
        elif "n²" in lowered or "n^2" in lowered or "n2" in lowered:
            topic_key = "on2"
        elif "big o" in lowered or "độ phức tạp" in lowered:
            topic_key = "bigo"
        elif "sắp xếp" in lowered or "sort" in lowered:
            topic_key = "sorting"
        elif "python" in lowered or "3.14" in lowered:
            topic_key = "python314"
        elif "elo" in lowered or "zpd" in lowered:
            topic_key = "elo"
        elif "sm-2" in lowered or "sm2" in lowered or "ôn tập" in lowered or "spaced" in lowered:
            topic_key = "sm2"
        elif any(greet in lowered for greet in ("xin chào", "chào", "hello", "hi")):
            topic_key = "greeting"

        match topic_key:
            case "greeting":
                return (
                    f"Xin chào {username}! Mình là Trợ giảng AI Nyvora (đang vận hành trên Python {self.python_version}). "
                    f"Với mức Elo hiện tại {elo_int} ({tier_name}), bạn muốn mình hỗ trợ ôn tập Python 3.14, "
                    "Cấu trúc dữ liệu & Giải thuật, Toán học hay Tiếng Anh hôm nay?"
                )
            case "ologn":
                if overall_elo < 1200:
                    return (
                        f"[Elo {elo_int} · Nhập môn] O(log n) nghĩa là mỗi bước bạn cắt đôi bài toán! "
                        "Ví dụ tìm một trang trong cuốn từ điển 1.024 trang bằng Binary Search: bạn mở giữa sách, "
                        "loại bỏ một nửa và lặp lại — chỉ mất tối đa log₂(1024) = 10 bước thay vì lật từng trang."
                    )
                return (
                    f"[Elo {elo_int} · {tier_name}] Độ phức tạp O(log n) xuất hiện khi không gian tìm kiếm giảm theo cấp số nhân "
                    "(điển hình là Binary Search, cây BST cân bằng, Heap push/pop). Với hệ thức truy hồi T(n) = T(n/2) + O(1), "
                    "theo Định lý Master ta thu được T(n) = Θ(log₂ n). Bạn thử nghĩ xem điều kiện tiên quyết của mảng để áp dụng Binary Search là gì?"
                )
            case "on2":
                return (
                    f"[Elo {elo_int} · {tier_name}] O(n²) thường xuất hiện khi có 2 vòng lặp lồng nhau duyệt qua n phần tử "
                    "(ví dụ Bubble Sort, Insertion Sort hoặc kiểm tra mọi cặp phần tử). Nếu n tăng gấp 10 lần, số phép toán tăng gấp 100 lần. "
                    "Trong Python 3.14, bạn thường có thể tối ưu O(n²) xuống O(n) bằng cấu trúc băm `dict` hoặc `set`!"
                )
            case "bigo":
                return (
                    f"[Elo {elo_int} · {tier_name}] Ký hiệu Big O đo tốc độ tăng trưởng thời gian/bộ nhớ của thuật toán khi kích thước dữ liệu n tiến ra vô cùng. "
                    "Thứ tự phổ biến từ nhanh đến chậm: O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ). "
                    "Bạn muốn mình lấy ví dụ code Python 3.14 minh họa cho mức độ phức tạp nào?"
                )
            case "sorting":
                return (
                    f"[Elo {elo_int} · {tier_name}] Các thuật toán sắp xếp cơ bản (Bubble, Selection, Insertion Sort) có độ phức tạp trung bình O(n²), "
                    "phù hợp để hiểu tư duy đổi chỗ. Trong thực tế, hàm `sorted()` và `.sort()` của Python sử dụng thuật toán **Timsort** "
                    "(kết hợp Merge Sort + Insertion Sort) đạt O(n log n) xấu nhất và O(n) trên dữ liệu gần như đã sắp xếp."
                )
            case "python314":
                return (
                    f"[Elo {elo_int} · {tier_name}] Hệ thống Chatbot Nyvora hiện đang chạy trực tiếp trên **Python {self.python_version}**! "
                    "Python 3.14 mang lại nhiều nâng cấp nổi bật như: đánh giá chú thích kiểu trễ mặc định (PEP 649), "
                    "Template Strings `t'...'` an toàn chống injection (PEP 750), trình thông dịch mới tăng tốc độ thực thi và cải thiện thông báo lỗi cú pháp. "
                    "Bạn muốn luyện tập chủ đề Python nào tiếp theo?"
                )
            case "elo":
                return (
                    f"Nyvora chấm điểm năng lực động bằng thuật toán Elo (hiện tại của bạn: {elo_int}). "
                    "Hệ thống tự động chọn câu hỏi nằm trong Vùng Phát triển Gần nhất (ZPD) giúp xác suất trả lời đúng của bạn duy trì ở ngưỡng vàng 70%–85%."
                )
            case "sm2":
                return (
                    "Thuật toán SM-2 (SuperMemo-2) trên Nyvora tính toán thời điểm bạn sắp quên kiến thức dựa trên độ chính xác và thời gian phản hồi, "
                    "từ đó giãn lịch ôn tập (1 ngày → 6 ngày → nhân theo hệ số dễ EF) giúp nhớ lâu hơn với thời gian ôn giảm ~40%."
                )
            case _:
                return (
                    f"[Trợ giảng AI Python {self.python_version} · Elo {elo_int}] Câu hỏi rất đáng suy ngẫm về: \"{message}\". "
                    "Để nắm chắc vấn đề này theo phương pháp chủ động, bạn hãy chia nhỏ bài toán thành 3 bước: "
                    "(1) Xác định đầu vào/đầu ra, (2) Viết ví dụ nhỏ kiểm chứng, (3) Đánh giá độ phức tạp. "
                    "Bạn có thể hỏi cụ thể hơn về Python 3.14, Big O, thuật toán sắp xếp hoặc làm bài Quiz để mình phân tích sâu hơn nhé!"
                )


chatbot_service = NyvoraChatbotService()
