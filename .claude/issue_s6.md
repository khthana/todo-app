## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

When a `RecurringTask` is transitioned to `COMPLETED`, TaskService automatically spawns the next Occurrence. The new Occurrence inherits `title`, `description`, `recurrence_pattern`, `tags`, and `end_recurrence_date` from the completed task, but starts with no dependencies and status `PENDING`. `next_occurrence` is calculated via the appropriate RecurrenceStrategy. If `end_recurrence_date` is set and the calculated `next_occurrence` would fall after it, no new Occurrence is spawned.

## Acceptance criteria

- [ ] Transitioning a RecurringTask to `COMPLETED` creates a new RecurringTask with `status: PENDING`
- [ ] The spawned Occurrence has the correct `next_occurrence` (calculated by the matching RecurrenceStrategy)
- [ ] The spawned Occurrence inherits `title`, `description`, `recurrence_pattern`, `tags`, and `end_recurrence_date`
- [ ] The spawned Occurrence has no dependencies
- [ ] When `next_occurrence` would fall after `end_recurrence_date`, no Occurrence is spawned and the transition still succeeds
- [ ] The spawned Occurrence is retrievable via `GET /tasks/`
- [ ] Tests cover spawning for each recurrence pattern and the end-of-series termination case

## Blocked by

- https://github.com/khthana/todo-app/issues/4 (StateTransition)
- https://github.com/khthana/todo-app/issues/6 (RecurringTask CRUD)
