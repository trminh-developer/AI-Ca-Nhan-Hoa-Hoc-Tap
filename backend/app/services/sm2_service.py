"""
SuperMemo-2 (SM-2) Spaced Repetition Service (Python 3.14.x).

Chống lại đường cong quên lãng Hermann Ebbinghaus:
- Chất lượng nhớ q in [0, 5] dựa trên tính đúng/sai, thời gian phản hồi t (ms) và số lần gợi ý.
- Hệ số dễ (Easiness Factor - EF):
    EF(new) = max(1.3, EF(old) + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
- Khoảng cách ôn tập (Interval I theo ngày):
    I(1) = 1, I(2) = 6, I(n) = round(I(n-1) * EF) với n >= 3
    Nếu q < 3 (quên kiến thức): Reset về I = 1, Repetition = 0.
"""

from datetime import datetime, timedelta, timezone


class SM2Service:
    """Engine thuật toán lặp lại ngắt quãng SuperMemo-2 (SM-2)."""

    FAST_THRESHOLD_MS: int = 10000
    SLOW_THRESHOLD_MS: int = 30000
    MIN_EASINESS_FACTOR: float = 1.3

    def calculate_quality(
        self,
        is_correct: bool,
        time_spent_ms: int,
        hints_used: int = 0,
        expected_success: float = 0.675,
    ) -> int:
        """
        Đánh giá chất lượng ghi nhớ q in [0, 5]:
        - 5: Đúng, phản hồi nhanh (<= 10s), không dùng gợi ý
        - 4: Đúng, tốc độ trung bình (10s - 30s)
        - 3: Đúng nhưng mất nhiều thời gian (> 30s) hoặc dùng gợi ý
        - 2: Sai nhưng không dùng gợi ý và phản hồi nhanh
        - 1: Sai mất nhiều thời gian (> 30s)
        - 0: Sai và đã dùng nhiều gợi ý (>= 2)
        """
        safe_time = max(0, int(time_spent_ms))
        safe_hints = max(0, int(hints_used))

        if not is_correct:
            if safe_hints >= 2:
                return 0
            if safe_time > self.SLOW_THRESHOLD_MS:
                return 1
            return 2

        if safe_hints == 0 and safe_time <= self.FAST_THRESHOLD_MS:
            return 5
        if safe_hints == 0 and safe_time <= self.SLOW_THRESHOLD_MS:
            return 4
        return 3

    def update(
        self,
        quality: int,
        repetitions: int,
        interval: int,
        easiness_factor: float,
    ) -> tuple[int, int, float]:
        """
        Cập nhật (new_interval_days, new_repetitions, new_easiness_factor) theo chuẩn SM-2.
        """
        q = max(0, min(5, int(quality)))
        reps = max(0, int(repetitions))
        prev_interval = max(1, int(interval))
        ef = max(self.MIN_EASINESS_FACTOR, float(easiness_factor))

        delta_ef = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
        new_ef = max(self.MIN_EASINESS_FACTOR, round(ef + delta_ef, 4))

        if q < 3:
            return 1, 0, new_ef

        if reps == 0:
            new_interval = 1
        elif reps == 1:
            new_interval = 6
        else:
            new_interval = max(1, int(round(prev_interval * new_ef)))

        return new_interval, reps + 1, new_ef

    def get_next_review_date(self, interval_days: int) -> datetime:
        """Tính thời điểm ôn tập tiếp theo (UTC) dựa trên khoảng cách ngày I."""
        return datetime.now(timezone.utc) + timedelta(days=max(1, int(interval_days)))


SM2Engine = SM2Service
sm2_service = SM2Service()
sm2_engine = sm2_service
