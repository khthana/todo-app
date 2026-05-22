from __future__ import annotations

from datetime import datetime

import pytest

from app.services.recurrence import DailyStrategy, MonthlyStrategy, WeeklyStrategy


def test_daily_strategy_advances_one_day():
    result = DailyStrategy().calculate_next(datetime(2024, 3, 15, 10, 0, 0))
    assert result == datetime(2024, 3, 16, 10, 0, 0)


def test_weekly_strategy_advances_seven_days():
    result = WeeklyStrategy().calculate_next(datetime(2024, 3, 15, 10, 0, 0))
    assert result == datetime(2024, 3, 22, 10, 0, 0)


def test_monthly_strategy_advances_one_calendar_month():
    result = MonthlyStrategy().calculate_next(datetime(2024, 3, 15, 10, 0, 0))
    assert result == datetime(2024, 4, 15, 10, 0, 0)


def test_monthly_strategy_clamps_to_last_day_of_month():
    # Jan 31 → Feb 28 (2024 is a leap year, so Feb 29)
    result = MonthlyStrategy().calculate_next(datetime(2024, 1, 31, 0, 0, 0))
    assert result == datetime(2024, 2, 29, 0, 0, 0)
