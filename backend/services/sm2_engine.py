"""
SM-2 Spaced Repetition Engine - Thuật toán lặp lại ngắt quãng SuperMemo 2.

SM-2 giúp tối ưu hóa lịch ôn tập:
- Câu hỏi trả lời đúng nhiều lần -> khoảng cách ôn tập tăng dần
- Câu hỏi trả lời sai -> reset về ôn lại ngay
- Hệ số dễ (EF) điều chỉnh theo chất lượng trả lời
"""

from datetime import date, timedelta


class SM2Engine:
    """
    Engine thuật toán SM-2 (SuperMemo 2) cho lặp lại ngắt quãng.
    
    Tham khảo: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method
    
    Quy trình:
    1. Đánh giá chất lượng trả lời (quality: 0-5)
    2. Cập nhật EF (Easiness Factor), interval, repetitions
    3. Tính ngày ôn tập tiếp theo
    """

    # Ngưỡng thời gian (ms) để đánh giá tốc độ trả lời
    FAST_THRESHOLD_MS = 5000    # < 5 giây = nhanh
    SLOW_THRESHOLD_MS = 30000   # > 30 giây = chậm

    # Hệ số dễ tối thiểu
    MIN_EASINESS_FACTOR = 1.3

    def calculate_quality(
        self,
        is_correct: bool,
        time_spent_ms: int,
        hints_used: int = 0,
        expected_success: float = 0.5,
    ) -> int:
        """
        Tính chất lượng trả lời (0-5) dựa trên nhiều yếu tố.
        
        Thang đo SM-2:
            5 - Hoàn hảo: trả lời đúng, nhanh, không dùng gợi ý
            4 - Tốt: trả lời đúng nhưng hơi chậm
            3 - Chấp nhận được: trả lời đúng nhưng khó khăn
            2 - Khó khăn: trả lời sai nhưng gần đúng / biết câu trả lời
            1 - Sai: trả lời sai, không nhớ rõ
            0 - Hoàn toàn sai: không có ý niệm gì về câu trả lời
        
        Args:
            is_correct: Trả lời có đúng không
            time_spent_ms: Thời gian trả lời (mili giây)
            hints_used: Số gợi ý đã sử dụng
            expected_success: Xác suất thành công dự kiến (từ Elo)
            
        Returns:
            Chất lượng trả lời (0-5)
        """
        if not is_correct:
            # Sai: quality từ 0-2 tùy thuộc vào thời gian suy nghĩ
            if time_spent_ms < self.FAST_THRESHOLD_MS:
                return 0  # Sai nhanh = không biết gì
            elif time_spent_ms < self.SLOW_THRESHOLD_MS:
                return 1  # Sai sau khi suy nghĩ = có hiểu biết phần nào
            else:
                return 2  # Sai sau thời gian dài = gần biết nhưng chưa chắc
        
        # Đúng: quality từ 3-5
        quality = 5  # Bắt đầu từ mức cao nhất
        
        # Trừ điểm nếu dùng gợi ý
        if hints_used > 0:
            quality -= min(hints_used, 2)  # Tối đa trừ 2 điểm cho gợi ý
        
        # Trừ điểm nếu trả lời chậm
        if time_spent_ms > self.SLOW_THRESHOLD_MS:
            quality -= 1  # Chậm = khó khăn
        
        # Trừ điểm nếu câu hỏi được dự đoán là dễ nhưng mất nhiều thời gian
        if expected_success > 0.8 and time_spent_ms > self.FAST_THRESHOLD_MS * 2:
            quality -= 1  # Câu dễ nhưng mất thời gian = chưa thành thạo
        
        # Đảm bảo quality nằm trong khoảng 3-5 cho đáp án đúng
        return max(3, min(5, quality))

    def update(
        self,
        quality: int,
        repetitions: int,
        interval: int,
        easiness_factor: float,
    ) -> tuple[int, int, float]:
        """
        Cập nhật thông số SM-2 sau mỗi lần ôn tập.
        
        Thuật toán SM-2:
        - Nếu quality >= 3 (đạt):
            - repetitions = 0 -> interval = 1 ngày
            - repetitions = 1 -> interval = 6 ngày  
            - repetitions > 1 -> interval = interval * EF
        - Nếu quality < 3 (không đạt):
            - Reset repetitions = 0, interval = 1
        - EF = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        
        Args:
            quality: Chất lượng trả lời (0-5)
            repetitions: Số lần ôn tập thành công liên tiếp hiện tại
            interval: Khoảng cách ôn tập hiện tại (ngày)
            easiness_factor: Hệ số dễ hiện tại
            
        Returns:
            Tuple (new_interval, new_repetitions, new_easiness_factor)
        """
        # Cập nhật Easiness Factor
        new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(self.MIN_EASINESS_FACTOR, new_ef)

        if quality >= 3:
            # Trả lời đạt: tăng khoảng cách ôn tập
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = round(interval * new_ef)
            
            new_repetitions = repetitions + 1
        else:
            # Trả lời không đạt: reset về đầu
            new_interval = 1
            new_repetitions = 0
        
        # Giới hạn interval tối đa 365 ngày (1 năm)
        new_interval = min(new_interval, 365)
        
        return new_interval, new_repetitions, new_ef

    def get_next_review_date(self, interval: int) -> date:
        """
        Tính ngày ôn tập tiếp theo.
        
        Args:
            interval: Khoảng cách ôn tập (ngày)
            
        Returns:
            Ngày ôn tập tiếp theo
        """
        return date.today() + timedelta(days=interval)


# Singleton instance
sm2_engine = SM2Engine()
