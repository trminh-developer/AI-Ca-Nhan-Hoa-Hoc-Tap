"""
Adaptive Socratic AI Tutor Service (Python 3.14.x + Google GenAI SDK).

Thiết kế Sư phạm Socratic 3 tầng Elo:
- Tầng 1: Elo < 1200 (Novice/Beginner)     -> Ngôn từ mộc mạc, chia nhỏ bài toán, câu hỏi gợi mở vi mô.
- Tầng 2: 1200 <= Elo <= 1800 (Intermediate)-> Thách thức phát hiện lỗ hổng logic, gợi ý từ khóa cốt lõi.
- Tầng 3: Elo > 1800 (Advanced/Master)     -> Thảo luận tối ưu hóa, kiến trúc giải thuật, edge cases.

Tích hợp Sliding Window Context (10 lượt gần nhất) và Rule-based Pedagogical Fallback Engine.
"""

from dataclasses import dataclass
import platform
import sys
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]

from app.core.config import GEMINI_API_KEY, GEMINI_MODEL

type ConversationTurn = dict[str, str]


@dataclass(slots=True)
class TutorReplyResult:
    """Kết quả phản hồi từ Trợ giảng AI Socratic."""
    reply: str
    engine: str
    python_version: str
    socratic_tier: str


class SocraticTutorService:
    """Dịch vụ Trợ giảng AI Socratic chạy trên Python 3.14.x."""

    SLIDING_WINDOW_SIZE: int = 10

    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL) -> None:
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name or "gemini-2.5-flash"
        self.python_version = platform.python_version()
        self._client: Any = None

        if self.api_key and genai is not None:
            try:
                if self.api_key.startswith("AQ."):
                    self._client = genai.Client(vertexai=True, api_key=self.api_key)
                else:
                    self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def is_ai_configured(self) -> bool:
        return self._client is not None

    def get_runtime_info(self) -> dict[str, str | bool]:
        return {
            "service": "nyvora-socratic-tutor",
            "language": "Python",
            "python_version": self.python_version,
            "python_series": f"{sys.version_info.major}.{sys.version_info.minor}",
            "sdk": "google-genai",
            "model": self.model_name,
            "ai_configured": self.is_ai_configured,
        }

    @staticmethod
    def resolve_socratic_tier(elo: float) -> tuple[str, str]:
        """
        Phân 3 tầng Socratic Prompting theo điểm Elo:
        - < 1200      : Novice/Beginner
        - 1200..1800  : Intermediate
        - > 1800      : Advanced/Master
        """
        if elo < 1200.0:
            return (
                "Novice/Beginner (Elo < 1200)",
                (
                    "Giải thích bằng ngôn từ mộc mạc, trực quan kèm ví dụ đời thường. "
                    "Chia nhỏ bài toán thành các bước nhỏ và kết thúc bằng 1 câu hỏi gợi mở vi mô dễ trả lời."
                ),
            )
        if elo <= 1800.0:
            return (
                "Intermediate (Elo 1200-1800)",
                (
                    "Không đưa ngay toàn bộ lời giải cuối cùng. Hãy giải thích bản chất khái niệm, "
                    "đưa gợi ý từ khóa/công thức cốt lõi (dùng LaTeX $...$) và đặt câu hỏi Socratic "
                    "thách thức người học tự phát hiện bước tiếp theo."
                ),
            )
        return (
            "Advanced/Master (Elo > 1800)",
            (
                "Thảo luận ở cấp độ tối ưu hóa giải thuật, phân tích độ phức tạp tiệm cận, "
                "kiến trúc hệ thống, tư duy phản biện và các trường hợp biên (edge cases)."
            ),
        )

    def build_system_instruction(self, username: str, overall_elo: float) -> str:
        """Tạo System Prompt Socratic cá nhân hóa theo Elo."""
        tier_label, pedagogy_directive = self.resolve_socratic_tier(overall_elo)
        return (
            f"Bạn là Trợ giảng AI Socratic của nền tảng học tập thích ứng Nyvora (vận hành trên Python {self.python_version}). "
            f"Người học: '{username}' | Điểm năng lực Elo: {int(overall_elo)} | Phân tầng: {tier_label}.\n"
            f"Chỉ dẫn sư phạm Socratic: {pedagogy_directive}\n"
            "Quy tắc định dạng: Sử dụng Markdown rõ ràng, bọc công thức toán trong ký hiệu LaTeX `$công_thức$` "
            "và bọc đoạn mã nguồn trong khối ```python ... ``` chuẩn Python 3.14.x."
        )

    def generate_reply(
        self,
        user_message: str,
        username: str = "Học viên",
        overall_elo: float = 1200.0,
        history: list[ConversationTurn] | None = None,
    ) -> TutorReplyResult:
        """Sinh phản hồi Socratic qua `google-genai` hoặc Rule-based Pedagogical Fallback Engine."""
        cleaned_msg = user_message.strip()
        tier_label, _ = self.resolve_socratic_tier(overall_elo)

        if not cleaned_msg:
            return TutorReplyResult(
                reply="Bạn hãy nhập câu hỏi hoặc chủ đề cần mình gợi mở nhé!",
                engine="python-3.14-validator",
                python_version=self.python_version,
                socratic_tier=tier_label,
            )

        window_turns = (history or [])[-self.SLIDING_WINDOW_SIZE:]

        if self._client is not None and types is not None:
            contents: list[Any] = []
            for turn in window_turns:
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
                        temperature=0.65,
                    ),
                )
                if response and response.text:
                    return TutorReplyResult(
                        reply=response.text.strip(),
                        engine=f"google-genai/{self.model_name}",
                        python_version=self.python_version,
                        socratic_tier=tier_label,
                    )
            except Exception:
                pass

        fallback_reply = self._generate_pedagogical_fallback(
            message=cleaned_msg,
            username=username,
            overall_elo=overall_elo,
            tier_label=tier_label,
        )
        return TutorReplyResult(
            reply=fallback_reply,
            engine="python-3.14-socratic-fallback",
            python_version=self.python_version,
            socratic_tier=tier_label,
        )

    def _generate_pedagogical_fallback(
        self,
        message: str,
        username: str,
        overall_elo: float,
        tier_label: str,
    ) -> str:
        """
        Rule-based Pedagogical Socratic Fallback Engine (Python 3.14 match/case)
        hỗ trợ hiển thị công thức LaTeX và khối lệnh Python 3.14.
        """
        lowered = message.lower()
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
        elif "đạo hàm" in lowered or "tích phân" in lowered or "toán" in lowered or "phương trình" in lowered:
            topic_key = "math"
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
                    f"Xin chào **{username}**! Mình là **Trợ giảng AI Socratic** của Nyvora "
                    f"(vận hành trên `Python {self.python_version}`).\n\n"
                    f"- **Trình độ hiện tại**: Elo `{elo_int}` — *{tier_label}*\n"
                    "- Bạn muốn cùng mình phân tích bài toán **Lập trình Python 3.14**, **Giải tích & Đại số**, hay **Tiếng Anh học thuật**?"
                )
            case "ologn":
                if overall_elo < 1200:
                    return (
                        f"**[Socratic · {tier_label}]** Hãy hình dung bạn tìm một từ trong cuốn từ điển 1.024 trang. "
                        "Nếu mở ngay trang chính giữa và bỏ đi một nửa cuốn sách ở mỗi bước, số bước tối đa chỉ là $\\log_2(1024) = 10$ bước!\n\n"
                        "```python\n"
                        "def binary_search_steps(n: int) -> int:\n"
                        "    steps = 0\n"
                        "    while n > 1:\n"
                        "        n //= 2\n"
                        "        steps += 1\n"
                        "    return steps\n"
                        "```\n"
                        "👉 **Câu hỏi gợi mở**: Nếu danh sách chưa được sắp xếp tăng dần, cách chia đôi này còn chính xác không? Vì sao?"
                    )
                return (
                    f"**[Socratic · {tier_label}]** Độ phức tạp $\\mathcal{{O}}(\\log_2 n)$ xuất hiện khi kích thước không gian tìm kiếm giảm theo cấp số nhân: "
                    "$T(n) = T(n/2) + \\mathcal{O}(1) \\implies T(n) = \\Theta(\\log_2 n)$.\n\n"
                    "👉 **Câu hỏi tư duy**: Khi cài đặt Binary Search với chỉ số `mid = (left + right) // 2`, trong Python 3.14 có nguy cơ tràn số nguyên (integer overflow) như C++/Java không?"
                )
            case "on2":
                return (
                    f"**[Socratic · {tier_label}]** Độ phức tạp bậc hai $\\mathcal{{O}}(n^2)$ thường sinh ra từ hai vòng lặp lồng nhau duyệt qua $n$ phần tử, "
                    "tổng số phép so sánh là $\\frac{{n(n-1)}}{{2}} = \\mathcal{{O}}(n^2)$.\n\n"
                    "```python\n"
                    "# Cặp phần tử có tổng bằng target: O(n^2) -> tối ưu xuống O(n) với set\n"
                    "def has_pair_sum(nums: list[int], target: int) -> bool:\n"
                    "    seen: set[int] = set()\n"
                    "    for x in nums:\n"
                    "        if (target - x) in seen:\n"
                    "            return True\n"
                    "        seen.add(x)\n"
                    "    return False\n"
                    "```\n"
                    "👉 **Câu hỏi gợi mở**: Vì sao việc tra cứu `(target - x) in seen` trên `set` lại giúp giảm độ phức tạp từ $\\mathcal{O}(n^2)$ xuống $\\mathcal{O}(n)$?"
                )
            case "bigo":
                return (
                    f"**[Socratic · {tier_label}]** Ký hiệu **Big O** đặc trưng cho cận trên tiệm cận của hàm chi phí khi $n \\to \\infty$:\n"
                    "$$\\mathcal{O}(1) < \\mathcal{O}(\\log n) < \\mathcal{O}(n) < \\mathcal{O}(n \\log n) < \\mathcal{O}(n^2) < \\mathcal{O}(2^n)$$\n\n"
                    "👉 **Câu hỏi gợi mở**: Nếu một thuật toán mất $T(n) = 3n^2 + 100n + 50$ phép toán, hạng tử nào quyết định tốc độ tăng trưởng khi $n = 10^6$?"
                )
            case "sorting":
                return (
                    f"**[Socratic · {tier_label}]** Các thuật toán sắp xếp cơ sở như *Bubble Sort*, *Insertion Sort* có độ phức tạp trung bình $\\mathcal{{O}}(n^2)$, "
                    "trong khi *Merge Sort* và *Timsort* (thuật toán mặc định của `sorted()` trong Python 3.14) đạt cận tối ưu $\\mathcal{O}(n \\log n)$.\n\n"
                    "👉 **Câu hỏi Socratic**: Trong trường hợp mảng đầu vào **đã gần như được sắp xếp**, vì sao *Insertion Sort* hoặc *Timsort* lại chạy gần đạt $\\mathcal{O}(n)$?"
                )
            case "math":
                return (
                    f"**[Socratic · {tier_label}]** Trong Giải tích & Đại số, hãy luôn bắt đầu từ định nghĩa gốc. "
                    "Chẳng hạn, đạo hàm biểu diễn tốc độ biến thiên tức thời:\n"
                    "$$f'(x) = \\lim_{\\Delta x \\to 0} \\frac{f(x + \\Delta x) - f(x)}{\\Delta x}$$\n\n"
                    "👉 **Câu hỏi gợi mở**: Bạn hãy cho mình biết biểu thức hoặc phương trình cụ thể bạn đang giải để chúng ta phân tích từng bước nhé!"
                )
            case "python314":
                return (
                    f"**[Socratic · {tier_label}]** Hệ thống Trợ giảng Nyvora đang thực thi trực tiếp trên **Python {self.python_version}**! "
                    "Python 3.14 nổi bật với **PEP 649** (đánh giá trễ annotations), **PEP 750** (Template Strings `t'...'`), và cú pháp `type Alias = ...`.\n\n"
                    "```python\n"
                    "type EloScore = float\n"
                    "def classify_tier(elo: EloScore) -> str:\n"
                    "    match elo:\n"
                    "        case x if x < 1200: return 'Novice'\n"
                    "        case x if x <= 1800: return 'Intermediate'\n"
                    "        case _: return 'Master'\n"
                    "```\n"
                    "👉 **Câu hỏi gợi mở**: Bạn muốn luyện tập viết hàm Python 3.14 cho chủ đề nào tiếp theo?"
                )
            case "elo":
                return (
                    f"**[Cơ chế Dual Elo & ZPD]** Điểm năng lực của bạn ($R_L = {elo_int}$) và độ khó câu hỏi ($R_I$) được cập nhật theo xác suất kỳ vọng:\n"
                    "$$E_L = \\frac{1}{1 + 10^{(R_I - R_L)/400}}, \\quad R_L^{(new)} = R_L + K_L \\cdot (S - E_L)$$\n"
                    "Hệ thống chọn câu hỏi trong vùng **ZPD** ($0.60 \\le E_L \\le 0.75$) để bạn luôn đạt trạng thái học tập tối ưu (*Flow*)."
                )
            case "sm2":
                return (
                    "**[Cơ chế SM-2 Spaced Repetition]** Hệ số dễ $EF$ được hiệu chỉnh sau mỗi lần ôn theo chất lượng trả lời $q \\in [0, 5]$:\n"
                    "$$EF^{(new)} = \\max\\left(1.3, EF + 0.1 - (5 - q)\\cdot(0.08 + (5 - q)\\cdot 0.02)\\right)$$\n"
                    "Nhờ đó câu bạn đã nhớ kỹ sẽ giãn chu kỳ ôn ($1 \\to 6 \\to 15 \\to 38$ ngày), còn câu trả lời sai ($q < 3$) sẽ được đưa về ôn lại ngay sau $1$ ngày."
                )
            case _:
                return (
                    f"**[Socratic AI · Python {self.python_version} · {tier_label}]** Câu hỏi rất thú vị về: *\"{message}\"*.\n\n"
                    "Theo phương pháp vấn đáp Socratic, trước khi đi tới đáp án cuối cùng, chúng ta hãy tách vấn đề thành 2 câu hỏi nhỏ:\n"
                    "1. **Giả thiết cốt lõi (Input/Điều kiện)** của bài toán này là gì?\n"
                    "2. Nếu thử với một **ví dụ nhỏ nhất ($n=1$ hoặc $n=2$)** thì kết quả biến đổi như thế nào?\n\n"
                    "Bạn hãy thử nêu suy nghĩ bước 1, mình sẽ gợi mở ngay bước tiếp theo nhé!"
                )


tutor_service = SocraticTutorService()
chatbot_service = tutor_service
