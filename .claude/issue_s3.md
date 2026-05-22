## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Add a `POST /tasks/{id}/transition` endpoint that drives Task lifecycle state changes. TaskService validates the requested transition against an allowed-transitions map and rejects illegal moves. Terminal states (`COMPLETED`, `CANCELLED`) cannot transition further. The endpoint delegates to TaskService, which raises `TaskNotFoundError` on missing tasks — already mapped to 404 by the exception handler from Slice 1.

Allowed transitions:
- `PENDING` → `IN_PROGRESS`
- `PENDING` → `CANCELLED`
- `IN_PROGRESS` → `COMPLETED`
- `IN_PROGRESS` → `CANCELLED`
- `IN_PROGRESS` → `PENDING`

## Acceptance criteria

- [ ] `POST /tasks/{id}/transition` with `{ "to_status": "in_progress" }` transitions the task and returns the updated task
- [ ] Transitioning from a terminal state (`COMPLETED` or `CANCELLED`) returns 422
- [ ] Transitioning to a disallowed state (e.g. `PENDING` → `COMPLETED`) returns 422
- [ ] `POST /tasks/{id}/transition` on a non-existent task returns 404
- [ ] Tests cover all valid transitions and rejection of all invalid ones

## Blocked by

- https://github.com/khthana/todo-app/issues/3
