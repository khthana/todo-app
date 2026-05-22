# PRD: Advanced Task Management API — Full Rebuild

> GitHub Issue: https://github.com/khthana/todo-app/issues/1

## Problem Statement

The current API is a minimal Todo CRUD system with a flat `todos` table and a single `completed` boolean. It cannot represent the real complexity users face when managing work: tasks with hard deadlines, tasks that repeat on a schedule, tasks that are blocked by other tasks, or tasks that need to be grouped and filtered. There is no concept of lifecycle states, no safety net against completing a task whose dependencies are unfinished, and no protection against circular dependency graphs.

## Solution

Rebuild the backend as a fully-featured Task Management API that models three distinct Task types (`StandardTask`, `DeadlineTask`, `RecurringTask`), enforces correct StateTransitions, detects and rejects Dependency cycles, automatically spawns the next Occurrence when a RecurringTask is completed, and groups Tasks via Tags. The API exposes a clean, typed REST surface backed by a layered architecture (Router → TaskService → TaskRepository) with domain exceptions mapped to appropriate HTTP status codes.

## User Stories

1. As an API consumer, I want to create a StandardTask with a title and description, so that I can track work that has no deadline.
2. As an API consumer, I want to create a DeadlineTask with a `due_date`, so that I can track work that must be finished before a specific datetime.
3. As an API consumer, I want to create a RecurringTask with a `recurrence_pattern` (DAILY, WEEKLY, MONTHLY) and an optional `end_recurrence_date`, so that repeating work is automatically rescheduled.
4. As an API consumer, I want to retrieve a Task by ID and receive type-specific fields (e.g., `due_date` on a DeadlineTask), so that clients can render the correct UI for each type.
5. As an API consumer, I want to list all Tasks, so that I can display an overview of the work queue.
6. As an API consumer, I want to filter Tasks by `status` and by `tag`, so that I can focus on relevant subsets.
7. As an API consumer, I want to update a Task's title or description, so that I can correct mistakes or add detail.
8. As an API consumer, I want to delete a Task, so that irrelevant tasks can be removed.
9. As an API consumer, I want to transition a Task from `PENDING` to `IN_PROGRESS`, so that I can communicate that work has started.
10. As an API consumer, I want to transition a Task from `IN_PROGRESS` to `COMPLETED`, so that I can record that work is done.
11. As an API consumer, I want to transition a Task to `CANCELLED`, so that I can remove it from active tracking without losing audit history.
12. As an API consumer, I want the API to reject invalid StateTransitions (e.g., `COMPLETED` to anything), so that task lifecycle integrity is preserved.
13. As an API consumer, I want the API to prevent me from marking a Task as `COMPLETED` when it has unfinished Dependencies, so that prerequisite work is not skipped.
14. As an API consumer, I want to add a Dependency relationship between two Tasks (Task A blocked by Task B), so that execution order is enforced.
15. As an API consumer, I want the API to reject a new Dependency that would create a cycle, so that the dependency graph stays acyclic.
16. As an API consumer, I want to remove a Dependency between two Tasks, so that I can update the work plan when prerequisites change.
17. As an API consumer, I want to see which Tasks are blocking a given Task, so that I understand what must be done first.
18. As an API consumer, I want completing a RecurringTask to automatically create the next Occurrence, so that I never have to manually recreate repeating work.
19. As an API consumer, I want the next Occurrence of a RecurringTask to inherit the title, description, recurrence pattern, and tags of the completed Occurrence, so that repeated tasks are consistent.
20. As an API consumer, I want the next Occurrence of a RecurringTask to start with empty Dependencies, so that each Occurrence is independently completable.
21. As an API consumer, I want no new Occurrence to spawn when a RecurringTask with an `end_recurrence_date` is completed after that date, so that finite series terminate automatically.
22. As an API consumer, I want to query whether a DeadlineTask is overdue, so that I can surface past-due items to the user.
23. As an API consumer, I want to extend the `due_date` on a DeadlineTask, so that I can accommodate scope changes without recreating the task.
24. As an API consumer, I want to attach Tags to a Task when creating or updating it, so that I can categorize work.
25. As an API consumer, I want Tags to be auto-created by name if they do not already exist, so that I do not need a separate tag-creation step.
26. As an API consumer, I want to list all Tags in the system, so that I can offer a tag picker in a client UI.
27. As an API consumer, I want renaming a Tag to immediately apply to every Task using that Tag, so that categorization stays consistent.
28. As an API consumer, I want to receive a `404 Not Found` when I request a Task or Tag that does not exist, so that missing-resource errors are unambiguous.
29. As an API consumer, I want to receive a `400 Bad Request` when I attempt to create a Dependency that would form a cycle, so that I know the graph constraint was violated.
30. As an API consumer, I want to receive a `422 Unprocessable Entity` when I attempt to complete a blocked Task, so that I know which business rule was violated.
31. As an API consumer, I want to receive a `400 Bad Request` when I supply an invalid RecurrencePattern, so that schema errors are reported clearly.
32. As an API consumer, I want internal errors to return a safe `500` response without stack traces, so that implementation details are not leaked.
33. As an API consumer, I want interactive API documentation at `/docs`, so that I can explore endpoints without reading source code.

## Implementation Decisions

### Architecture

Four-layer architecture: **Routers** (HTTP boundary) → **TaskService** (business logic) → **TaskRepository / TagRepository** (data access) → **SQLAlchemy Models** (persistence). Routers know nothing about database sessions; TaskService knows nothing about HTTP.

Domain exceptions (`DomainException`, `TaskNotFoundError`, `DependencyCycleError`, `TaskBlockedError`, `InvalidRecurrencePatternError`) are raised by TaskService and caught by FastAPI exception handlers in the Router layer, which map them to appropriate HTTP status codes.

### Database Schema (Single Table Inheritance — ADR-0001)

A single `tasks` table holds all Task types with a `type` discriminator column (`standard`, `deadline`, `recurring`). Columns specific to one type are NULL for other types (`due_date`, `reminder_time` only set for DeadlineTask; `recurrence_pattern`, `next_occurrence`, `end_recurrence_date` only set for RecurringTask). An association table `task_dependencies` (blocker_id, blocked_id) stores Dependency relationships. A `tags` table and a `task_tags` join table implement the many-to-many Tag relationship.

### Task Hierarchy

- `Task` is the SQLAlchemy polymorphic base using STI (`__mapper_args__` with `polymorphic_on=type`).
- `StandardTask`, `DeadlineTask`, `RecurringTask` are mapped subclasses that add type-specific columns and behavior methods.
- `TaskStatus` enum: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`.
- `RecurrencePattern` enum: `DAILY`, `WEEKLY`, `MONTHLY`.

### TaskService — Key Behaviors

- **StateTransition**: validate against an allowed-transitions map before persisting. Terminal states (`COMPLETED`, `CANCELLED`) may not transition further.
- **Dependency cycle detection**: DFS traversal of the existing dependency graph on every `add_dependency` call. Reject with `DependencyCycleError` if the new edge would create a cycle.
- **Completion guard**: before allowing `IN_PROGRESS → COMPLETED`, verify all Dependencies have status `COMPLETED`. `CANCELLED` dependencies are treated as still-blocking (they are not `COMPLETED`).
- **Occurrence spawning**: when a RecurringTask transitions to `COMPLETED`, calculate `next_occurrence` via the appropriate RecurrenceStrategy. If `next_occurrence` is before `end_recurrence_date` (or `end_recurrence_date` is null), create a new RecurringTask copying title, description, recurrence_pattern, tags, and end_recurrence_date — but not dependencies.

### RecurrenceStrategy (Strategy Pattern)

A `RecurrenceStrategy` protocol defines `calculate_next(current: datetime) -> datetime`. Concrete implementations: `DailyStrategy` (+1 day), `WeeklyStrategy` (+7 days), `MonthlyStrategy` (+1 calendar month). A `RecurrenceStrategyFactory` maps `RecurrencePattern` enum values to strategy instances, making it possible to add new patterns without modifying existing code.

### Overdue

`DeadlineTask.is_overdue()` is a read-only property comparing `due_date` to `datetime.utcnow()`. It is included in the `DeadlineTaskResponse` schema. Being overdue does not block StateTransitions.

### Tag Management

Tags are identified by name (case-insensitive, stripped). TagRepository upserts by name: returns an existing Tag or creates a new one. Tags are passed as a list of name strings in Task Create/Update payloads. The service resolves names to Tag entities before saving. No standalone POST/DELETE tag endpoints — only `GET /tags/` to list all tags.

### API Surface

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/tasks/` | Create a task (type-discriminated body) |
| GET | `/tasks/` | List tasks (optional filter: `status`, `tag`) |
| GET | `/tasks/{id}` | Get a task by ID |
| PATCH | `/tasks/{id}` | Update title, description, type-specific fields, tags |
| DELETE | `/tasks/{id}` | Delete a task |
| POST | `/tasks/{id}/transition` | Trigger a StateTransition (`{ "to_status": "..." }`) |
| POST | `/tasks/{id}/dependencies` | Add a Dependency (`{ "blocker_id": ... }`) |
| DELETE | `/tasks/{id}/dependencies/{blocker_id}` | Remove a Dependency |
| GET | `/tags/` | List all tags |

### Schemas

- Discriminated union on `type` field for Create and Response schemas to enable per-type validation and serialization.
- `TaskResponse` includes `is_overdue` boolean for `DeadlineTask` responses.
- `TaskResponse` includes the full list of Tag names and dependency IDs.

## Testing Decisions

Good tests verify **external behavior** — what the module does given inputs and preconditions — not how it does it internally. Tests should not assert on private methods, SQL queries, or ORM internals.

### TaskService (unit tests with in-memory SQLite)

- Valid and invalid StateTransitions for each status.
- Completing a Task whose Dependencies are all `COMPLETED` succeeds.
- Completing a Task with any non-`COMPLETED` Dependency raises `TaskBlockedError`.
- Adding a non-cyclic Dependency succeeds.
- Adding a Dependency that creates a cycle raises `DependencyCycleError`.
- Completing a RecurringTask spawns a new Occurrence with the correct `next_occurrence`.
- Completing a RecurringTask past `end_recurrence_date` does not spawn a new Occurrence.

### RecurrenceStrategy (pure unit tests)

- `DailyStrategy` advances by exactly one day.
- `WeeklyStrategy` advances by exactly seven days.
- `MonthlyStrategy` advances by exactly one calendar month (including edge cases: Jan 31 → Feb 28/29, end-of-month).

### TaskRepository (integration tests with in-memory SQLite)

- Create/read/update/delete Tasks of all three types.
- Tag upsert returns existing Tag on second call with same name.
- Querying Tasks by status and by Tag name returns correct subsets.
- Dependency rows are persisted and retrieved correctly.

### API Routers (end-to-end with FastAPI TestClient)

- Each endpoint returns the correct HTTP status and response shape for the happy path.
- `TaskNotFoundError` → `404`, `DependencyCycleError` → `400`, `TaskBlockedError` → `422`, `InvalidRecurrencePatternError` → `400`.
- Creating a RecurringTask and POSTing a `COMPLETED` transition returns a `200` and the spawned Occurrence is retrievable via `GET /tasks/`.

Prior art: the project uses `pytest`; test structure should follow the existing `tests/` layout.

## Out of Scope

- Authentication and authorization — all endpoints are unauthenticated.
- Reminder delivery (email, push notification) — `reminder_time` is stored but no dispatch mechanism is implemented.
- Pagination on list endpoints.
- Cron expression support for RecurrencePattern (only DAILY, WEEKLY, MONTHLY).
- Soft-delete or task archival — CANCELLED tasks remain in the database as audit trail; DELETE physically removes.
- Frontend / client application.
- Data migration from the existing `todos` table — the table will be dropped and replaced.

## Further Notes

- The `todos` table and all existing schemas will be removed as part of this rebuild. The `Todo` model, `TodoCreate`/`TodoUpdate`/`TodoResponse` schemas, and the `/todos/` router are all superseded.
- The domain glossary in `CONTEXT.md` defines canonical names (e.g., **Occurrence**, **Dependency**, **TagManagement**) — all implementation naming must match.
- ADR-0001 confirms the STI decision; no new ADR is needed for the approach described here.
- Python typing should be strict throughout (`from __future__ import annotations`, full type hints) to leverage FastAPI's automatic schema generation.
