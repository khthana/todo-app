## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Deliver a fully working CRUD cycle for `StandardTask` cutting through every layer. Create the `tasks` table using Single Table Inheritance with a `type` discriminator column (ADR-0001). Implement TaskRepository (create, get by ID, list, update, delete), TaskService (delegates CRUD, raises `TaskNotFoundError` on missing IDs), StandardTask Create/Update/Response Pydantic schemas, and `POST / GET / PATCH / DELETE /tasks/` router endpoints. All four layers must be covered by tests.

## Acceptance criteria

- [ ] `tasks` table exists with `id`, `type`, `title`, `description`, `status`, `created_at`, `updated_at` columns and a `type` discriminator
- [ ] `POST /tasks/` with `{ "type": "standard", ... }` returns 201 with the created task
- [ ] `GET /tasks/` returns a list of all tasks
- [ ] `GET /tasks/{id}` returns the task or 404 if not found
- [ ] `PATCH /tasks/{id}` performs a partial update (title, description) and returns the updated task
- [ ] `DELETE /tasks/{id}` removes the task and returns 204
- [ ] TaskService raises `TaskNotFoundError` for unknown IDs (maps to 404 via exception handler)
- [ ] TaskRepository, TaskService, and router all have tests

## Blocked by

- https://github.com/khthana/todo-app/issues/2
