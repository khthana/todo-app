## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Extend the Task system to support `DeadlineTask`. Add `due_date` and `reminder_time` columns to the `tasks` table (NULL for non-deadline types). Implement the `DeadlineTask` subclass with an `is_overdue` read-only property. Extend schemas with a `DeadlineTaskResponse` that includes `is_overdue`. Extend the router so `POST /tasks/` with `"type": "deadline"` creates a `DeadlineTask`, and `PATCH /tasks/{id}` allows updating `due_date`. Being overdue must not block any StateTransition.

## Acceptance criteria

- [ ] `POST /tasks/` with `{ "type": "deadline", "due_date": "..." }` creates a DeadlineTask and returns 201
- [ ] `GET /tasks/{id}` on a DeadlineTask includes `due_date`, `reminder_time`, and `is_overdue` in the response
- [ ] `is_overdue` is `true` when `due_date` is in the past, `false` otherwise
- [ ] `PATCH /tasks/{id}` can update `due_date` on a DeadlineTask
- [ ] A DeadlineTask that is overdue can still be transitioned to `COMPLETED` without error
- [ ] Tests cover `is_overdue` logic (past and future due dates) and CRUD for the deadline type

## Blocked by

- https://github.com/khthana/todo-app/issues/3
