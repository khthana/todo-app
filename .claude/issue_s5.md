## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Add `RecurringTask` support and the RecurrenceStrategy layer. Implement a `RecurrenceStrategy` protocol with `calculate_next(current: datetime) -> datetime`. Build three concrete strategies — `DailyStrategy` (+1 day), `WeeklyStrategy` (+7 days), `MonthlyStrategy` (+1 calendar month) — and a `RecurrenceStrategyFactory` that maps `RecurrencePattern` enum values (`DAILY`, `WEEKLY`, `MONTHLY`) to strategy instances. Add `recurrence_pattern`, `next_occurrence`, and `end_recurrence_date` columns to the `tasks` table (NULL for non-recurring types). Extend router and schemas so `POST /tasks/` with `"type": "recurring"` creates a `RecurringTask`. An invalid `recurrence_pattern` value raises `InvalidRecurrencePatternError` (maps to 400).

## Acceptance criteria

- [ ] `POST /tasks/` with `{ "type": "recurring", "recurrence_pattern": "DAILY", "next_occurrence": "..." }` creates a RecurringTask and returns 201
- [ ] `GET /tasks/{id}` on a RecurringTask includes `recurrence_pattern`, `next_occurrence`, and `end_recurrence_date`
- [ ] Providing an invalid `recurrence_pattern` returns 400
- [ ] `DailyStrategy` advances by exactly 1 day
- [ ] `WeeklyStrategy` advances by exactly 7 days
- [ ] `MonthlyStrategy` advances by 1 calendar month, handling end-of-month edge cases (e.g. Jan 31 → Feb 28/29)
- [ ] Strategy unit tests and RecurringTask CRUD integration tests both pass

## Blocked by

- https://github.com/khthana/todo-app/issues/3
