# Todo App — Project Guide

## Overview

Backend REST API สำหรับ Task Management application สร้างด้วย FastAPI + SQLite รองรับ task หลายประเภทพร้อม state transitions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.136+ |
| Database | SQLite (via SQLAlchemy 2.0) |
| Runtime | Python 3.13 |
| Package manager | uv |
| Server | Uvicorn |

## Project Structure

```
todo-app/
├── .claude/
│   ├── settings.json       ← Claude Code project permissions
│   └── commands/           ← Custom slash commands
├── app/
│   ├── main.py             ← FastAPI app entry point, exception handlers, creates DB tables
│   ├── database.py         ← SQLAlchemy engine, SessionLocal, get_db dependency
│   ├── models.py           ← ORM models (Task STI: Task, StandardTask, DeadlineTask, RecurringTask)
│   ├── schemas.py          ← Pydantic request/response schemas
│   ├── repositories/
│   │   └── tasks.py        ← TaskRepository — DB access only, no business logic
│   ├── services/
│   │   ├── tasks.py        ← TaskService — business logic, state transitions, exceptions
│   │   └── recurrence.py   ← RecurrenceStrategy protocol + Daily/Weekly/Monthly + factory
│   └── routers/
│       ├── todos.py        ← CRUD endpoints for /todos
│       └── tasks.py        ← CRUD + transition endpoints for /tasks
├── tests/
│   ├── conftest.py
│   ├── test_task_repository.py
│   ├── test_task_service.py
│   ├── test_tasks_router.py
│   ├── test_recurrence_strategies.py
│   └── test_todos.py
├── docs/
│   ├── adr/                ← Architecture Decision Records
│   └── agents/             ← Agent skill configuration docs
├── CONTEXT.md              ← Domain glossary (canonical terminology)
├── CLAUDE.md               ← This file
├── pyproject.toml
└── uv.lock
```

## Git Workflow

หลัง slice เสร็จทุกครั้ง ให้ทำตามลำดับนี้เสมอ:

1. **run tests** — `uv run pytest tests/ -q` ต้องผ่านทั้งหมดก่อน
2. **commit** — ใส่ `Closes #N` ใน commit message เพื่อให้ GitHub ปิด issue อัตโนมัติตอน push
3. **push** — ทันทีหลัง commit ไม่รอ

```bash
uv run pytest tests/ -q
git add <files>
git commit -m "Implement Slice N: <description>

Closes #N"
git push
```

> อย่าใช้ `gh issue close` โดยตรง — ให้ปิดผ่าน `Closes #N` ใน commit message แทน

## Common Commands

```bash
# Run dev server (hot reload)
uv run uvicorn app.main:app --reload

# Add a new package
uv add <package>

# Run with specific port
uv run uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/todos/` | List all todos |
| POST | `/todos/` | Create a new todo |
| GET | `/todos/{id}` | Get a todo by ID |
| PATCH | `/todos/{id}` | Update a todo |
| DELETE | `/todos/{id}` | Delete a todo |
| POST | `/tasks/` | Create a task — dispatch on `type`: `standard`, `deadline`, `recurring` (returns 201) |
| GET | `/tasks/` | List all tasks — optional `?status=` and `?tag=` query filters |
| GET | `/tasks/{id}` | Get a task by ID (404 if not found) |
| PATCH | `/tasks/{id}` | Partial update (title, description) |
| DELETE | `/tasks/{id}` | Delete a task (returns 204) |
| POST | `/tasks/{id}/transition` | Drive state transition — body: `{ "to_status": "..." }` (422 if disallowed) |
| POST | `/tasks/{id}/dependencies` | Add a blocker — body: `{ "blocker_id": N }` (400 if cycle) |
| DELETE | `/tasks/{id}/dependencies/{blocker_id}` | Remove a blocker |
| GET | `/tags/` | List all tags |

Interactive docs: `http://localhost:8000/docs`

## Database

- SQLite file: `todo.db` (auto-created on first run, gitignored)
- Tables are created automatically via `Base.metadata.create_all()` in `main.py`
- No migration tool — drop `todo.db` to reset schema during development

## Architecture Notes

- `get_db()` ใน `database.py` เป็น FastAPI dependency ที่ inject SQLAlchemy session เข้า route
- Schemas แยกเป็น `Create`, `Update`, `Response` เพื่อควบคุม input/output แต่ละ operation
- `TodoUpdate` / `StandardTaskUpdate` ใช้ fields เป็น `Optional` ทั้งหมดเพื่อรองรับ partial update (PATCH)
- Task layer ใช้ Repository pattern — `TaskRepository` (DB only) → `TaskService` (business logic) → router
- `TaskService` raise custom exceptions ที่ `main.py` map เป็น HTTP status: `TaskNotFoundError`→404, `InvalidTransitionError`→422, `InvalidRecurrencePatternError`→400
- State transitions ถูกควบคุมโดย `_ALLOWED` map ใน `TaskService` — terminal states (COMPLETED, CANCELLED) ออกไม่ได้
- Task model ใช้ Single Table Inheritance — ดู `docs/adr/0001-single-table-inheritance-for-task-types.md`
- RecurrenceStrategy pattern ใน `services/recurrence.py` — `DailyStrategy`, `WeeklyStrategy`, `MonthlyStrategy` (clamp end-of-month) + `RecurrenceStrategyFactory`
- `POST /tasks/` ใช้ Pydantic discriminated union บน `type` field เพื่อ dispatch ไปยัง `create_task`, `create_deadline_task`, หรือ `create_recurring_task`
- เมื่อ `RecurringTask` ถูก transition เป็น `COMPLETED` — `TaskService._spawn_next_occurrence()` จะสร้าง Occurrence ใหม่โดยอัตโนมัติ: `next_occurrence` คำนวณผ่าน `RecurrenceStrategyFactory`; หาก `next_occurrence > end_recurrence_date` จะไม่ spawn (end-of-series)
- Dependency system: association table `task_dependencies` (blocker_id → blocked_id); `Task.blockers` relationship; `TaskService.add_dependency()` ทำ DFS cycle check ก่อน (`DependencyCycleError`→400); `transition_task` to `COMPLETED` ตรวจว่า blocker ทุกตัวมี status `completed` (`TaskBlockedError`→422); `Task.blocker_ids` property expose ใน `TaskResponse`
- Tag system: `Tag` model + `task_tags` join table + `Task.tags` relationship; `TagRepository.upsert(name)` (case-insensitive, stripped); `TaskService` รับ `tags: list[str]` ใน create/update; `GET /tasks/` รองรับ `?status=` และ `?tag=` filter; `Task.tag_names` property expose ใน `TaskResponse`; router แยก `app/routers/tags.py`

## Agent skills

### Issue tracker

Issues live in GitHub Issues (`khthana/todo-app`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
