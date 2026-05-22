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
│   ├── models.py           ← ORM models (Task STI hierarchy: Task, StandardTask)
│   ├── schemas.py          ← Pydantic request/response schemas
│   ├── repositories/
│   │   └── tasks.py        ← TaskRepository — DB access only, no business logic
│   ├── services/
│   │   └── tasks.py        ← TaskService — business logic, state transitions, exceptions
│   └── routers/
│       ├── todos.py        ← CRUD endpoints for /todos
│       └── tasks.py        ← CRUD + transition endpoints for /tasks
├── tests/
│   ├── conftest.py
│   ├── test_task_repository.py
│   ├── test_task_service.py
│   ├── test_tasks_router.py
│   └── test_todos.py
├── docs/
│   ├── adr/                ← Architecture Decision Records
│   └── agents/             ← Agent skill configuration docs
├── CONTEXT.md              ← Domain glossary (canonical terminology)
├── CLAUDE.md               ← This file
├── pyproject.toml
└── uv.lock
```

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
| POST | `/tasks/` | Create a StandardTask (returns 201) |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{id}` | Get a task by ID (404 if not found) |
| PATCH | `/tasks/{id}` | Partial update (title, description) |
| DELETE | `/tasks/{id}` | Delete a task (returns 204) |
| POST | `/tasks/{id}/transition` | Drive state transition — body: `{ "to_status": "..." }` (422 if disallowed) |

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
- `TaskService` raise custom exceptions (`TaskNotFoundError`, `InvalidTransitionError`) ที่ `main.py` map เป็น 404/422
- State transitions ถูกควบคุมโดย `_ALLOWED` map ใน `TaskService` — terminal states (COMPLETED, CANCELLED) ออกไม่ได้
- Task model ใช้ Single Table Inheritance — ดู `docs/adr/0001-single-table-inheritance-for-task-types.md`

## Agent skills

### Issue tracker

Issues live in GitHub Issues (`khthana/todo-app`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
