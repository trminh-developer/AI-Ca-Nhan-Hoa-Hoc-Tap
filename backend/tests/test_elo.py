"""
Unit Tests cho Thuật toán Dual Elo Rating (Item Response Theory / Logistic Variant).
"""

import math
from types import SimpleNamespace

from app.services.elo_service import EloEngine


def test_expected_score_equal_ratings():
    """Khi R_L == R_I, xác suất kỳ vọng trả lời đúng phải bằng đúng 0.50."""
    engine = EloEngine()
    assert math.isclose(engine.expected_score(1500.0, 1500.0), 0.5, rel_tol=1e-9)


def test_expected_score_400_difference():
    """Khi R_L - R_I = 400, E_L = 1 / (1 + 10^-1) = 10/11 ≈ 0.90909."""
    engine = EloEngine()
    prob = engine.expected_score(1900.0, 1500.0)
    assert math.isclose(prob, 10.0 / 11.0, rel_tol=1e-6)


def test_expected_score_symmetry():
    """Tính chất đối xứng: E_L(R_L, R_I) + E_L(R_I, R_L) == 1.0."""
    engine = EloEngine()
    p1 = engine.expected_score(1350.0, 1620.0)
    p2 = engine.expected_score(1620.0, 1350.0)
    assert math.isclose(p1 + p2, 1.0, rel_tol=1e-9)


def test_expected_score_extreme_overflow_safety():
    """Không bị OverflowError khi chênh lệch Elo cực lớn (+/- 50000)."""
    engine = EloEngine()
    high = engine.expected_score(50000.0, 1000.0)
    low = engine.expected_score(1000.0, 50000.0)
    assert 0.999 < high <= 1.0
    assert 0.0 <= low < 0.001


def test_dynamic_k_factor_scaling():
    """Hệ số K_L co giãn động theo số lần luyện tập của học viên."""
    engine = EloEngine(k_learner=32.0, k_item=16.0)
    assert engine.get_dynamic_k_learner(0) == 32.0
    assert engine.get_dynamic_k_learner(5) == 32.0
    assert engine.get_dynamic_k_learner(15) == 24.0
    assert engine.get_dynamic_k_learner(35) == 16.0


def test_update_ratings_correct_and_incorrect():
    """
    Kiểm tra công thức cập nhật Elo Kép:
    R_L(new) = R_L(old) + K_L * (S - E_L)
    R_I(new) = R_I(old) + K_I * (E_L - S)
    """
    engine = EloEngine(k_learner=32.0, k_item=16.0)

    # Trả lời đúng câu ngang sức (1500 vs 1500 -> E_L = 0.5)
    new_l, new_i = engine.update_ratings(1500.0, 1500.0, actual_score=1.0)
    assert math.isclose(new_l, 1516.0, rel_tol=1e-6)
    assert math.isclose(new_i, 1492.0, rel_tol=1e-6)

    # Trả lời sai câu ngang sức (S = 0.0)
    new_l_wrong, new_i_wrong = engine.update_ratings(1500.0, 1500.0, actual_score=0.0)
    assert math.isclose(new_l_wrong, 1484.0, rel_tol=1e-6)
    assert math.isclose(new_i_wrong, 1508.0, rel_tol=1e-6)


def test_zpd_optimal_content_selection():
    """Chọn câu hỏi nằm trong vùng phát triển gần nhất (0.60 <= E_L <= 0.75)."""
    engine = EloEngine()
    items = [
        SimpleNamespace(id=1, difficulty_elo=800.0),   # Quá dễ (E_L > 0.98)
        SimpleNamespace(id=2, difficulty_elo=1380.0),  # Trong vùng ZPD cho R_L = 1500 (E_L ≈ 0.666)
        SimpleNamespace(id=3, difficulty_elo=1410.0),  # Trong vùng ZPD cho R_L = 1500 (E_L ≈ 0.626)
        SimpleNamespace(id=4, difficulty_elo=2200.0),  # Quá khó (E_L < 0.02)
    ]
    selected = engine.select_optimal_content(1500.0, items, max_items=2)
    selected_ids = {item.id for item in selected}
    assert selected_ids == {2, 3}


def test_xp_calculation():
    """Tính điểm XP thưởng khi trả lời đúng và khuyến khích khi trả lời sai."""
    engine = EloEngine()
    assert engine.calculate_xp(16.0, True) > 10
    assert engine.calculate_xp(-16.0, False) == 2
