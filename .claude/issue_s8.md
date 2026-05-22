## Parent

https://github.com/khthana/todo-app/issues/1

## What to build

Add Tag management and task filtering. Create a `tags` table and a `task_tags` many-to-many join table. Implement TagRepository with an upsert-by-name operation (case-insensitive, stripped) so callers never need to pre-create tags. Task Create and Update payloads accept a `tags` list of name strings; TaskService resolves names to Tag entities before saving. Renaming a Tag (via `PATCH /tags/{id}`) propagates to all Tasks using it automatically. Add a `GET /tags/` endpoint listing all tags. Extend `GET /tasks/` to support `?status=` and `?tag=` query params for filtering.

## Acceptance criteria

- [ ] `POST /tasks/` with `"tags": ["work", "urgent"]` creates the task with those tags (auto-creating any that don't exist)
- [ ] `GET /tasks/{id}` response includes the list of tag names
- [ ] `PATCH /tasks/{id}` with a new `tags` list replaces the task's tags
- [ ] `GET /tags/` returns all tags in the system
- [ ] `GET /tasks/?tag=work` returns only tasks tagged with "work"
- [ ] `GET /tasks/?status=pending` returns only tasks with that status
- [ ] Tag upsert returns the same Tag entity on repeated calls with the same name (case-insensitive)
- [ ] Tests cover tag auto-creation, tag filtering, status filtering, and the upsert idempotency

## Blocked by

- https://github.com/khthana/todo-app/issues/3 (StandardTask CRUD)

