"""
Elo Rating Engine - Thuật toán xếp hạng Elo cho học tập thích ứng.

Elo Rating được sử dụng để:
1. Đánh giá trình độ học sinh (Learner Elo)
2. Đánh giá độ khó câu hỏi (Item Difficulty Elo)
3. Chọn nội dung phù hợp trong Vùng Phát triển Gần nhất (ZPD)
"""

import math
from typing import Optional


class EloEngine:
    """
    Engine tính toán Elo Rating cho hệ thống học tập thích ứng.
    
    Thuật toán Elo được chuyển thể từ cờ vua sang giáo dục:
    - Learner (học sinh) "đấu" với Question (câu hỏi)
    - Trả lời đúng = Learner thắng, sai = Learner thua
    - K-factor quyết định tốc độ thay đổi rating
    """

    def __init__(self, k_factor: int = 32, initial_rating: float = 1500.0):
        """
        Khởi tạo Elo Engine.
        
        Args:
            k_factor: Hệ số K - ảnh hưởng đến biên độ thay đổi Elo mỗi lần.
                      K lớn = thay đổi nhanh, K nhỏ = thay đổi chậm (ổn định hơn).
            initial_rating: Rating khởi đầu cho người dùng/câu hỏi mới.
        """
        self.k_factor = k_factor
        self.initial_rating = initial_rating

    def expected_score(self, learner_rating: float, item_difficulty: float) -> float:
        """
        Tính xác suất thành công dự kiến của học sinh với câu hỏi.
        
        Sử dụng công thức logistic từ thuật toán Elo:
        E(A) = 1 / (1 + 10^((R_B - R_A) / 400))
        
        Args:
            learner_rating: Elo hiện tại của học sinh
            item_difficulty: Elo độ khó của câu hỏi
            
        Returns:
            Xác suất trả lời đúng (0.0 - 1.0)
        """
        exponent = (item_difficulty - learner_rating) / 400.0
        return 1.0 / (1.0 + math.pow(10, exponent))

    def update_ratings(
        self,
        learner_rating: float,
        item_difficulty: float,
        actual_score: float,
    ) -> tuple[float, float]:
        """
        Cập nhật Elo cho cả học sinh và câu hỏi sau khi tương tác.
        
        Args:
            learner_rating: Elo hiện tại của học sinh
            item_difficulty: Elo hiện tại của câu hỏi
            actual_score: Kết quả thực tế (1.0 = đúng, 0.0 = sai, 0.5 = bán phần)
            
        Returns:
            Tuple (new_learner_rating, new_item_difficulty)
        """
        expected = self.expected_score(learner_rating, item_difficulty)
        
        # Cập nhật Elo cho học sinh
        # Đúng khi khó -> tăng nhiều, sai khi dễ -> giảm nhiều
        learner_change = self.k_factor * (actual_score - expected)
        new_learner = learner_rating + learner_change
        
        # Cập nhật Elo cho câu hỏi (ngược lại với học sinh)
        # Học sinh giỏi trả lời đúng -> câu hỏi không quá khó -> giảm nhẹ
        item_change = self.k_factor * (expected - actual_score)
        new_item = item_difficulty + item_change
        
        # Giới hạn Elo trong khoảng hợp lý (100 - 3000)
        new_learner = max(100.0, min(3000.0, new_learner))
        new_item = max(100.0, min(3000.0, new_item))
        
        return new_learner, new_item

    def select_optimal_content(
        self,
        learner_elo: float,
        available_items: list,
        target_success: float = 0.75,
        zpd_low: float = 0.70,
        zpd_high: float = 0.85,
        max_items: int = 10,
    ) -> list:
        """
        Chọn nội dung tối ưu trong Vùng Phát triển Gần nhất (Zone of Proximal Development).
        
        Nguyên lý: Học sinh học hiệu quả nhất khi thành công ~75% thời gian.
        Quá dễ (>85%) = nhàm chán, Quá khó (<70%) = nản chí.
        
        Args:
            learner_elo: Elo hiện tại của học sinh
            available_items: Danh sách các item (cần có thuộc tính difficulty_elo)
            target_success: Xác suất thành công mục tiêu (mặc định 0.75)
            zpd_low: Ngưỡng dưới ZPD (mặc định 0.70)
            zpd_high: Ngưỡng trên ZPD (mặc định 0.85)
            max_items: Số lượng item tối đa trả về
            
        Returns:
            Danh sách item trong ZPD, sắp xếp theo độ gần target_success
        """
        scored_items = []
        
        for item in available_items:
            # Lấy difficulty_elo từ object hoặc dict
            if hasattr(item, "difficulty_elo"):
                item_elo = item.difficulty_elo
            elif isinstance(item, dict):
                item_elo = item.get("difficulty_elo", self.initial_rating)
            else:
                continue
            
            # Tính xác suất thành công
            success_prob = self.expected_score(learner_elo, item_elo)
            
            # Chỉ chọn item trong ZPD
            if zpd_low <= success_prob <= zpd_high:
                # Tính khoảng cách đến target để sắp xếp
                distance = abs(success_prob - target_success)
                scored_items.append((distance, success_prob, item))
        
        # Sắp xếp theo khoảng cách đến target (gần nhất trước)
        scored_items.sort(key=lambda x: x[0])
        
        # Nếu không có item nào trong ZPD, mở rộng phạm vi
        if not scored_items:
            return self._fallback_selection(learner_elo, available_items, target_success, max_items)
        
        return [item for _, _, item in scored_items[:max_items]]

    def _fallback_selection(
        self,
        learner_elo: float,
        available_items: list,
        target_success: float,
        max_items: int,
    ) -> list:
        """
        Phương án dự phòng khi không có item nào trong ZPD.
        Chọn các item gần target_success nhất.
        """
        scored_items = []
        
        for item in available_items:
            if hasattr(item, "difficulty_elo"):
                item_elo = item.difficulty_elo
            elif isinstance(item, dict):
                item_elo = item.get("difficulty_elo", self.initial_rating)
            else:
                continue
            
            success_prob = self.expected_score(learner_elo, item_elo)
            distance = abs(success_prob - target_success)
            scored_items.append((distance, success_prob, item))
        
        scored_items.sort(key=lambda x: x[0])
        return [item for _, _, item in scored_items[:max_items]]

    def get_difficulty_label(self, elo: float) -> str:
        """
        Phân loại độ khó dựa trên Elo, ánh xạ theo Bloom's Taxonomy.
        
        Args:
            elo: Điểm Elo của câu hỏi
            
        Returns:
            Nhãn độ khó bằng tiếng Việt
        """
        if elo < 800:
            return "Rất dễ - Nhớ (Bloom 1)"
        elif elo < 1100:
            return "Dễ - Hiểu (Bloom 2)"
        elif elo < 1400:
            return "Trung bình - Áp dụng (Bloom 3)"
        elif elo < 1700:
            return "Khó - Phân tích (Bloom 4)"
        elif elo < 2000:
            return "Rất khó - Đánh giá (Bloom 5)"
        else:
            return "Cực khó - Sáng tạo (Bloom 6)"

    def calculate_xp(self, elo_change: float, is_correct: bool) -> int:
        """
        Tính điểm kinh nghiệm (XP) dựa trên thay đổi Elo.
        
        Args:
            elo_change: Mức thay đổi Elo
            is_correct: Có trả lời đúng không
            
        Returns:
            Điểm XP kiếm được (luôn >= 0)
        """
        if not is_correct:
            return max(1, int(abs(elo_change) * 0.1))  # XP an ủi
        
        base_xp = 10
        bonus = int(abs(elo_change) * 0.5)
        return base_xp + bonus


# Singleton instance cho toàn ứng dụng
elo_engine = EloEngine(k_factor=32, initial_rating=1500.0)
