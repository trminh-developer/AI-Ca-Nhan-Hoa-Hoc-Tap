"""
Unit Tests cho Thuật toán Lặp lại Ngắt quãng SuperMemo-2 (SM-2 Spaced Repetition).
"""

import math
from datetime import datetime, timezone

from app.services.sm2_service import SM2Engine


def test_sm2_interval_progression():
    """
    Kiểm tra chuỗi khoảng cách ôn tập chuẩn SM-2 khi nhớ tốt (q >= 3):
    I(1) = 1 ngày, I(2) = 6 ngày, I(3) = round(6 * EF).
    """
    sm2 = SM2Engine()

    # Lần 1 (repetitions = 0 -> 1)
    i1, r1, ef1 = sm2.update(quality=4, repetitions=0, interval=1, easiness_factor=2.5)
    assert i1 == 1
    assert r1 == 1
    assert math.isclose(ef1, 2.5, rel_tol=1e-6)

    # Lần 2 (repetitions = 1 -> 2)
    i2, r2, ef2 = sm2.update(quality=4, repetitions=r1, interval=i1, easiness_factor=ef1)
    assert i2 == 6
    assert r2 == 2
    assert math.isclose(ef2, 2.5, rel_tol=1e-6)

    # Lần 3 (repetitions = 2 -> 3): round(6 * 2.5) = 15 ngày
    i3, r3, ef3 = sm2.update(quality=4, repetitions=r2, interval=i2, easiness_factor=ef2)
    assert i3 == 15
    assert r3 == 3


def test_sm2_forgetting_resets_interval():
    """Khi q < 3 (quên kiến thức), SM-2 phải reset I = 1 và repetitions = 0."""
    sm2 = SM2Engine()
    interval, reps, ef = sm2.update(quality=1, repetitions=4, interval=35, easiness_factor=2.5)
    assert interval == 1
    assert reps == 0
    assert ef >= 1.3


def test_sm2_easiness_factor_floor():
    """Hệ số dễ EF không bao giờ được giảm xuống dưới ngưỡng tối thiểu 1.3."""
    sm2 = SM2Engine()
    ef = 1.35
    for _ in range(5):
        _, _, ef = sm2.update(quality=0, repetitions=2, interval=6, easiness_factor=ef)
    assert math.isclose(ef, 1.3, rel_tol=1e-6)


def test_sm2_calculate_quality_heuristics():
    """Đánh giá điểm chất lượng q (0..5) theo đúng/sai, thời gian và gợi ý."""
    sm2 = SM2Engine()
    assert sm2.calculate_quality(is_correct=True, time_spent_ms=5000, hints_used=0) == 5
    assert sm2.calculate_quality(is_correct=True, time_spent_ms=20000, hints_used=0) == 4
    assert sm2.calculate_quality(is_correct=True, time_spent_ms=50000, hints_used=1) == 3
    assert sm2.calculate_quality(is_correct=False, time_spent_ms=8000, hints_used=0) == 2
    assert sm2.calculate_quality(is_correct=False, time_spent_ms=40000, hints_used=0) == 1
    assert sm2.calculate_quality(is_correct=False, time_spent_ms=10000, hints_used=2) == 0


def test_sm2_next_review_date():
    """Ngày ôn tập tiếp theo phải lớn hơn thời điểm hiện tại."""
    sm2 = SM2Engine()
    next_dt = sm2.get_next_review_date(6)
    assert next_dt > datetime.now(timezone.utc)
