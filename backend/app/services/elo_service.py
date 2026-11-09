"""
Dual Elo Rating System Service (Python 3.14.x).

Chuyển hóa lý thuyết Item Response Theory (IRT) thành biến thể Elo thích nghi
thời gian thực với độ phức tạp O(1):
- Xác suất kỳ vọng: E_L = 1 / (1 + 10^((R_I - R_L) / 400))
- Hiệu chuẩn kép:
    R_L(new) = R_L(old) + K_L * (S - E_L)
    R_I(new) = R_I(old) + K_I * (E_L - S)
- Hệ số K_L co giãn động theo số lần luyện tập (K=32 cho người mới, K=16 khi ổn định).
"""

import math
from typing import Any

type RatingPair = tuple[float, float]


class EloService:
    """Engine tính toán Dual Elo Rating cho hệ thống học tập thích ứng Nyvora."""

    MIN_ELO: float = 100.0
    MAX_ELO: float = 3000.0

    def __init__(
        self,
        k_factor: float = 32.0,
        k_factor_stable: float = 16.0,
        k_factor_item: float = 16.0,
        initial_rating: float = 1500.0,
        k_learner: float | None = None,
        k_item: float | None = None,
    ) -> None:
        self.k_factor = float(k_learner if k_learner is not None else k_factor)
        self.k_factor_stable = float(k_factor_stable)
        self.k_factor_item = float(k_item if k_item is not None else k_factor_item)
        self.initial_rating = float(initial_rating)

    @property
    def k_learner(self) -> float:
        return self.k_factor

    @k_learner.setter
    def k_learner(self, val: float) -> None:
        self.k_factor = float(val)

    @property
    def k_item(self) -> float:
        return self.k_factor_item

    @k_item.setter
    def k_item(self, val: float) -> None:
        self.k_factor_item = float(val)

    def get_dynamic_k_factor(self, total_attempts: int = 0) -> float:
        """
        Tính hệ số K_L co giãn động theo số lượt tương tác của người học:
        - < 10 lượt  : K = k_factor (mặc định 32.0) để hội tụ nhanh năng lực thực
        - 10..29 lượt: K = trung bình cộng (24.0)
        - >= 30 lượt : K = k_factor_stable (mặc định 16.0) để ổn định điểm Elo
        """
        if total_attempts < 0:
            total_attempts = 0
        if total_attempts < 10:
            return self.k_factor
        if total_attempts < 30:
            return (self.k_factor + self.k_factor_stable) / 2.0
        return self.k_factor_stable

    def get_dynamic_k_learner(self, total_attempts: int = 0) -> float:
        return self.get_dynamic_k_factor(total_attempts)

    def calculate_expected_score(self, learner_rating: float, item_difficulty: float) -> float:
        """
        Tính xác suất kỳ vọng trả lời đúng E_L theo công thức logistic:
        E_L = 1 / (1 + 10^((R_I - R_L) / 400))
        Bảo vệ chống tràn số (OverflowError) và chia cho 0.
        """
        diff = float(item_difficulty) - float(learner_rating)
        exponent = max(-10.0, min(10.0, diff / 400.0))
        denominator = 1.0 + math.pow(10.0, exponent)
        if denominator <= 0.0:
            return 0.5
        return 1.0 / denominator

    def expected_score(self, learner_rating: float, item_difficulty: float) -> float:
        return self.calculate_expected_score(learner_rating, item_difficulty)

    def update_ratings(
        self,
        learner_rating: float,
        item_difficulty: float,
        actual_score: float,
        learner_attempts: int = 0,
        k_learner: float | None = None,
        k_item: float | None = None,
    ) -> RatingPair:
        """
        Cập nhật đồng thời Elo của học viên (R_L) và độ khó câu hỏi (R_I).
        """
        clamped_score = max(0.0, min(1.0, float(actual_score)))
        expected = self.calculate_expected_score(learner_rating, item_difficulty)

        active_k_l = float(k_learner) if k_learner is not None else self.get_dynamic_k_factor(learner_attempts)
        active_k_i = float(k_item) if k_item is not None else self.k_factor_item

        learner_change = active_k_l * (clamped_score - expected)
        item_change = active_k_i * (expected - clamped_score)

        new_learner = max(self.MIN_ELO, min(self.MAX_ELO, float(learner_rating) + learner_change))
        new_item = max(self.MIN_ELO, min(self.MAX_ELO, float(item_difficulty) + item_change))

        return round(new_learner, 2), round(new_item, 2)

    def select_optimal_content(
        self,
        learner_elo: float,
        available_items: list[Any],
        target_success: float = 0.675,
        zpd_low: float = 0.60,
        zpd_high: float = 0.75,
        max_items: int = 10,
    ) -> list[Any]:
        """
        Chọn danh sách câu hỏi nằm trong Vùng Phát triển Gần nhất (ZPD: 0.60 <= E_L <= 0.75).
        """
        if not available_items or max_items <= 0:
            return []

        zpd_items: list[tuple[Any, float]] = []
        acceptable_items: list[tuple[Any, float]] = []
        all_scored: list[tuple[Any, float]] = []

        for item in available_items:
            item_elo = getattr(item, "difficulty_elo", self.initial_rating)
            expected = self.calculate_expected_score(learner_elo, item_elo)
            distance = abs(expected - target_success)
            all_scored.append((item, distance))

            if zpd_low <= expected <= zpd_high:
                zpd_items.append((item, distance))
            elif 0.40 <= expected <= 0.85:
                acceptable_items.append((item, distance))

        zpd_items.sort(key=lambda pair: pair[1])
        if len(zpd_items) >= max_items:
            return [item for item, _ in zpd_items[:max_items]]

        selected = [item for item, _ in zpd_items]
        selected_ids = {id(item) for item in selected}

        acceptable_items.sort(key=lambda pair: pair[1])
        for item, _ in acceptable_items:
            if len(selected) >= max_items:
                break
            if id(item) not in selected_ids:
                selected.append(item)
                selected_ids.add(id(item))

        if len(selected) < max_items:
            all_scored.sort(key=lambda pair: pair[1])
            for item, _ in all_scored:
                if len(selected) >= max_items:
                    break
                if id(item) not in selected_ids:
                    selected.append(item)
                    selected_ids.add(id(item))

        return selected

    def calculate_xp(self, elo_change: float, is_correct: bool) -> int:
        """Tính điểm kinh nghiệm (XP) thưởng sau mỗi lượt trả lời."""
        if not is_correct:
            return 2
        bonus = max(0, int(round(elo_change)))
        return 10 + bonus


EloEngine = EloService
elo_service = EloService()
elo_engine = elo_service
