## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Add the Dependency system: a `task_dependencies` association table (blocker_id → blocked_id), two new endpoints (`POST /tasks/{id}/dependencies` and `DELETE /tasks/{id}/dependencies/{blocker_id}`), and two business rules enforced by TaskService:

1. **Cycle detection** — on every `add_dependency` call, perform a DFS traversal of the existing dependency graph. If the new edge would create a cycle, raise `DependencyCycleError` (maps to 400).
2. **Completion guard** — when transitioning a Task to `COMPLETED`, verify that every Task in its blocker list has status `COMPLETED`. A `CANCELLED` blocker is still considered blocking. Raise `TaskBlockedError` (maps to 422) if the guard fails.

## Acceptance criteria

- [ ] `POST /tasks/{id}/dependencies` with `{ "blocker_id": N }` adds the dependency and returns the updated task
- [ ] `DELETE /tasks/{id}/dependencies/{blocker_id}` removes the dependency and returns the updated task
- [ ] Adding a dependency that creates a cycle returns 400
- [ ] Transitioning a Task to `COMPLETED` when any blocker is not `COMPLETED` returns 422
- [ ] A `CANCELLED` blocker is treated as still-blocking (not COMPLETED)
- [ ] Transitioning to `COMPLETED` succeeds when all blockers are `COMPLETED`
- [ ] `GET /tasks/{id}` response includes the list of blocker IDs
- [ ] Tests cover cycle detection (including multi-hop cycles), the completion guard, and the remove-dependency path

## Blocked by

- https://github.com/khthana/todo-app/issues/4 (StateTransition)

