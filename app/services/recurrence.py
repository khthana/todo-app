from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Protocol


class RecurrenceStrategy(Protocol):
    def calculate_next(self, current: datetime) -> datetime: ...


class DailyStrategy:
    def calculate_next(self, current: datetime) -> datetime:
        return current + timedelta(days=1)


class WeeklyStrategy:
    def calculate_next(self, current: datetime) -> datetime:
        return current + timedelta(days=7)


class MonthlyStrategy:
    def calculate_next(self, current: datetime) -> datetime:
        month = current.month % 12 + 1
        year = current.year + (current.month // 12)
        day = min(current.day, calendar.monthrange(year, month)[1])
        return current.replace(year=year, month=month, day=day)


_STRATEGIES: dict[str, RecurrenceStrategy] = {
    "DAILY": DailyStrategy(),
    "WEEKLY": WeeklyStrategy(),
    "MONTHLY": MonthlyStrategy(),
}


class RecurrenceStrategyFactory:
    @staticmethod
    def get(pattern: str) -> RecurrenceStrategy:
        strategy = _STRATEGIES.get(pattern)
        if strategy is None:
            raise KeyError(pattern)
        return strategy
