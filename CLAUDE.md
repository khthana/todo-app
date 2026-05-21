# Todo App — Project Guide

## Overview

Backend REST API สำหรับ Todo application สร้างด้วย FastAPI + SQLite

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
│   ├── main.py             ← FastAPI app entry point, creates DB tables on startup
│   ├── database.py         ← SQLAlchemy engine, SessionLocal, get_db dependency
│   ├── models.py           ← ORM models
│   ├── schemas.py          ← Pydantic request/response schemas
│   └── routers/
│       └── todos.py        ← CRUD endpoints for /todos
├── requirements/           ← Project requirements documents
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

Interactive docs: `http://localhost:8000/docs`

## Database

- SQLite file: `todo.db` (auto-created on first run, gitignored)
- Tables are created automatically via `Base.metadata.create_all()` in `main.py`
- No migration tool — drop `todo.db` to reset schema during development

## Architecture Notes

- `get_db()` ใน `database.py` เป็น FastAPI dependency ที่ inject SQLAlchemy session เข้า route
- Schemas แยกเป็น `Create`, `Update`, `Response` เพื่อควบคุม input/output แต่ละ operation
- `TodoUpdate` ใช้ fields เป็น `Optional` ทั้งหมดเพื่อรองรับ partial update (PATCH)
