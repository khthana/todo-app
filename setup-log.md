# Setup Log — Todo App

บันทึกขั้นตอนการ setup project ทั้งหมด เรียงตามลำดับที่ทำจริง

---

## 1. สร้าง Backend API Environment

**เครื่องมือที่เลือก:** FastAPI + SQLite + uv

### uv คืออะไร?
`uv` คือ Python package manager รุ่นใหม่ เร็วกว่า `pip` มาก และจัดการ virtual environment ให้อัตโนมัติ

### ขั้นตอน
```bash
# สร้าง project ใหม่ด้วย uv
uv init --no-readme

# ติดตั้ง dependencies หลัก
uv add fastapi "uvicorn[standard]" sqlalchemy
```

### ไฟล์ที่สร้าง
```
todo-app/
├── app/
│   ├── __init__.py
│   ├── main.py        ← FastAPI app + สร้าง DB tables ตอน startup
│   ├── database.py    ← SQLite engine + get_db dependency
│   ├── models.py      ← ORM model (Todo table)
│   ├── schemas.py     ← Pydantic schemas สำหรับ validate input/output
│   └── routers/
│       └── todos.py   ← CRUD endpoints ทั้งหมด
├── pyproject.toml     ← config ของ project และ dependencies
└── uv.lock            ← lock file (เหมือน package-lock.json ใน Node)
```

### API Endpoints ที่ได้
| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET | `/` | Health check |
| GET | `/todos/` | ดึง todo ทั้งหมด |
| POST | `/todos/` | สร้าง todo ใหม่ |
| GET | `/todos/{id}` | ดึง todo ตาม id |
| PATCH | `/todos/{id}` | อัปเดต todo (partial update) |
| DELETE | `/todos/{id}` | ลบ todo |

### วิธีรัน server
```bash
uv run uvicorn app.main:app --reload
# เปิด http://localhost:8000/docs เพื่อดู Swagger UI
```

---

## 2. ปรับปรุง Project Structure

เพิ่ม 3 สิ่งสำคัญ:

### `.claude/` — Claude Code project config
```
.claude/
├── settings.json   ← กำหนด permissions สำหรับ Claude Code
├── commands/       ← Custom slash commands (skills)
└── docs/           ← Supporting files ของแต่ละ skill
```

**settings.json** pre-allow commands ที่ใช้บ่อย เพื่อลด permission prompts:
```json
{
  "permissions": {
    "allow": ["Bash(uv run *)", "Bash(uv add *)", "Bash(git status)", ...]
  }
}
```

### `requirements/` — เก็บ requirement documents
ไว้วาง PRD, functional/non-functional requirements ของ project

### `CLAUDE.md` — Project guide สำหรับ Claude Code
ไฟล์นี้สำคัญมาก — Claude Code อ่านไฟล์นี้ทุกครั้งที่เริ่ม session เพื่อเข้าใจ project
เก็บ tech stack, project structure, common commands, API endpoints, architecture notes

---

## 3. ติดตั้ง Git

```bash
git init
git add .
git commit -m "Initial project setup: FastAPI + SQLite + uv"
```

**ทำไมต้องทำ git init ทีหลัง?**
เพราะต้องการ setup project structure ให้เรียบร้อยก่อน แล้วค่อย track ด้วย git

---

## 4. Sync กับ GitHub

```bash
git remote add origin https://github.com/khthana/todo-app.git
git push -u origin master
```

หลังจากนี้ใช้แค่ `git push` ได้เลย เพราะ branch `master` track `origin/master` แล้ว

---

## 5. ติดตั้ง Skills (Custom Slash Commands)

Skills คือ custom slash commands ที่เก็บใน `.claude/commands/` เป็นไฟล์ `.md`
เมื่อพิมพ์ `/ชื่อ-skill` ใน Claude Code มันจะโหลด prompt จากไฟล์นั้นมาใช้งาน

> **หมายเหตุสำคัญ:** Claude Code อ่านเฉพาะไฟล์ `.md` ที่อยู่ใน `.claude/commands/` โดยตรงเท่านั้น
> ถ้ามีไฟล์ใน subfolder มันจะ expose เป็น sub-command ด้วย (เช่น `/skill:subfile`)
> จึงแยก supporting files ไปไว้ที่ `.claude/docs/` แทน

### โครงสร้างสุดท้ายของ skills

```
.claude/
├── commands/                         ← Claude Code อ่านเป็น slash commands
│   ├── grill-with-docs.md            → /grill-with-docs
│   ├── setup-matt-pocock-skills.md   → /setup-matt-pocock-skills
│   ├── tdd.md                        → /tdd
│   ├── to-issues.md                  → /to-issues
│   ├── to-prd.md                     → /to-prd
│   ├── triage.md                     → /triage
│   └── diagnose.md                   → /diagnose
└── docs/                             ← Supporting files (ไม่ถูก expose เป็น command)
    ├── grill-with-docs/
    │   ├── ADR-FORMAT.md
    │   └── CONTEXT-FORMAT.md
    ├── setup-matt-pocock-skills/
    │   ├── domain.md
    │   ├── issue-tracker-github.md
    │   ├── issue-tracker-gitlab.md
    │   ├── issue-tracker-local.md
    │   └── triage-labels.md
    ├── tdd/
    │   ├── deep-modules.md
    │   ├── interface-design.md
    │   ├── mocking.md
    │   ├── refactoring.md
    │   └── tests.md
    ├── triage/
    │   ├── AGENT-BRIEF.md
    │   └── OUT-OF-SCOPE.md
    └── diagnose/
        └── hitl-loop.template.sh
```

### รายละเอียดแต่ละ Skill

#### `/grill-with-docs`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs

สอบสวน plan ของคุณทีละขั้น พร้อมตรวจสอบ terminology กับ codebase จริง
- อัปเดต `CONTEXT.md` (glossary) ทันทีที่ resolve term
- สร้าง ADR (Architecture Decision Record) เฉพาะเมื่อการตัดสินใจ hard to reverse จริงๆ

---

#### `/setup-matt-pocock-skills`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills

Setup config ที่ skills อื่นๆ ต้องการ ได้แก่:
- **Issue tracker** — GitHub / GitLab / Local markdown / Other
- **Triage labels** — mapping ชื่อ label จริงใน repo
- **Domain docs** — single-context หรือ multi-context

สร้างไฟล์ `docs/agents/` และเพิ่ม `## Agent skills` block ใน `CLAUDE.md`
**ต้องรัน skill นี้ก่อน** ใช้ `/to-issues`, `/to-prd`, `/triage`, `/tdd`

---

#### `/to-prd`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/to-prd

แปลง conversation context เป็น PRD (Product Requirements Document) แล้ว publish เป็น GitHub Issue อัตโนมัติ

PRD template ประกอบด้วย:
- Problem Statement / Solution
- User Stories (รายละเอียดมากๆ)
- Implementation Decisions
- Testing Decisions
- Out of Scope

---

#### `/to-issues`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/to-issues

แตก plan หรือ PRD ออกเป็น issues แบบ **vertical slice** (tracer bullet)
- แต่ละ issue ตัดผ่านทุก layer (schema → API → test) ครบในตัวเอง
- ระบุ **HITL** (Human-in-the-loop ต้องการคน) หรือ **AFK** (agent ทำได้คนเดียว)
- ถามผู้ใช้ยืนยัน granularity และ dependency ก่อน publish

---

#### `/tdd`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd

Test-Driven Development แบบ red-green-refactor ทีละ cycle

หลักสำคัญ:
- **ทดสอบ behavior ไม่ใช่ implementation** — test ต้องรอดแม้ refactor code ข้างใน
- **Vertical slice ทีละ 1** — เขียน 1 test → implement → ผ่านแล้วค่อย test ต่อไป
- **Mock เฉพาะ system boundary** — external API, database ไม่ใช่ internal code ของตัวเอง

---

#### `/triage`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/triage

จัดการ GitHub Issues ผ่าน state machine

Roles:
- **Category:** `bug` / `enhancement`
- **State:** `needs-triage` → `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`

ใช้ภาษาธรรมชาติได้เลย เช่น:
```
"show me what needs my attention"
"let's look at #5"
"move #3 to ready-for-agent"
```

เมื่อ issue ถึง `ready-for-agent` จะเขียน **Agent Brief** ที่ระบุ behavior + acceptance criteria ชัดเจน

---

#### `/diagnose`
**ที่มา:** https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnose

Debug แบบมีวินัย 6 phases:

| Phase | สิ่งที่ทำ |
|-------|----------|
| 1. Build feedback loop | สร้าง test/script ที่ reproduce bug ได้ reproducibly |
| 2. Reproduce | รันและยืนยันว่า bug เกิดจริง |
| 3. Hypothesise | สร้าง 3-5 hypothesis พร้อม prediction ที่ falsifiable |
| 4. Instrument | ทดสอบทีละ hypothesis เปลี่ยนตัวแปรทีละอัน |
| 5. Fix + regression test | เขียน test ก่อน fix แล้วค่อย fix |
| 6. Cleanup + post-mortem | ลบ debug code, เขียน commit message อธิบาย root cause |

---

## 6. รัน /setup-matt-pocock-skills

หลังจากติดตั้ง skill แล้ว รันเพื่อ config repo นี้:

**การตัดสินใจที่เลือก:**
- **Issue tracker:** GitHub Issues (ใช้ `gh` CLI)
- **Triage labels:** ใช้ default ทั้งหมด (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix)
- **Domain docs:** Single-context (CONTEXT.md + docs/adr/ ที่ root)

**ไฟล์ที่สร้างขึ้น:**
```
docs/agents/
├── issue-tracker.md    ← วิธีใช้ gh CLI สำหรับ repo นี้
├── triage-labels.md    ← mapping label names
└── domain.md           ← layout ของ domain docs
```

และเพิ่ม `## Agent skills` block ใน `CLAUDE.md`

---

## 7. เพิ่ม Testing, Linting, และ CI

### pytest — Test Framework
```bash
uv add --dev pytest pytest-asyncio httpx
uv run pytest          # รัน tests
uv run pytest -v       # verbose output
```

**ไฟล์ที่สร้าง:**
```
tests/
├── conftest.py        ← setup test database (SQLite in-memory แยกจาก production)
└── test_todos.py      ← 7 tests ครอบคลุมทุก endpoint
```

Tests ผ่านทั้งหมด 7/7:
- `test_health_check` — GET /
- `test_create_todo` — POST /todos/
- `test_list_todos` — GET /todos/
- `test_get_todo` — GET /todos/{id}
- `test_get_todo_not_found` — GET /todos/999 → 404
- `test_update_todo` — PATCH /todos/{id}
- `test_delete_todo` — DELETE /todos/{id}

---

### ruff — Linter + Formatter
```bash
uv add --dev ruff
uv run ruff check .    # ตรวจ code style
uv run ruff format .   # จัด format อัตโนมัติ
```

Config ใน `pyproject.toml`:
```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I"]  # Error, pyFlakes, Import sorting
```

---

### GitHub Actions CI
ไฟล์: `.github/workflows/ci.yml`

รัน lint + test อัตโนมัติทุกครั้งที่:
- push ไปที่ branch `master`
- สร้าง Pull Request เข้า `master`

```yaml
jobs:
  test:
    steps:
      - Checkout code
      - Install uv
      - Install dependencies
      - Lint with ruff
      - Run pytest
```

---

### .env + python-dotenv
```bash
uv add --dev python-dotenv
```

`.env.example` — template สำหรับ environment variables:
```
DATABASE_URL=sqlite:///./todo.db
```

> **วิธีใช้:** copy `.env.example` เป็น `.env` แล้วแก้ค่าตามต้องการ
> `.env` อยู่ใน `.gitignore` จะไม่ถูก commit ขึ้น git (เพราะอาจมี secrets)

---

## สรุป Project Structure สุดท้าย

```
todo-app/
├── .claude/
│   ├── settings.json
│   ├── commands/           ← Slash commands (7 skills)
│   └── docs/               ← Supporting files ของ skills
├── .github/
│   └── workflows/
│       └── ci.yml          ← GitHub Actions CI
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       └── todos.py
├── docs/
│   └── agents/             ← Config สำหรับ agent skills
├── requirements/           ← Project requirement documents
├── tests/
│   ├── conftest.py
│   └── test_todos.py
├── .env.example
├── .gitignore
├── CLAUDE.md
├── pyproject.toml
├── setup-log.md            ← ไฟล์นี้
└── uv.lock
```

## Commands ที่ใช้บ่อย

```bash
# รัน dev server
uv run uvicorn app.main:app --reload

# รัน tests
uv run pytest -v

# ตรวจ code style
uv run ruff check .

# เพิ่ม package
uv add <package-name>

# เพิ่ม dev package
uv add --dev <package-name>

# git workflow
git add .
git commit -m "message"
git push
```

## Slash Commands ที่มี

| Command | ใช้เมื่อ |
|---------|---------|
| `/setup-matt-pocock-skills` | ครั้งแรกหรือเปลี่ยน issue tracker |
| `/grill-with-docs` | อยากสอบสวน plan ก่อน implement |
| `/to-prd` | แปลง idea เป็น PRD แล้ว publish issue |
| `/to-issues` | แตก PRD เป็น issues ย่อยๆ |
| `/triage` | จัดการ/ตรวจสอบ GitHub Issues |
| `/tdd` | เขียน code แบบ test-first |
| `/diagnose` | debug bug แบบมีระบบ |
