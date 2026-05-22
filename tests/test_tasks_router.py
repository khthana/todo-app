from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(bind=_engine)


def _override_get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# B9
def test_post_tasks_returns_201_with_created_task(client):
    resp = client.post("/tasks/", json={"type": "standard", "title": "My task"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["title"] == "My task"
    assert data["type"] == "standard"
    assert data["status"] == "pending"


# B10
def test_get_tasks_returns_list(client):
    client.post("/tasks/", json={"type": "standard", "title": "A"})
    client.post("/tasks/", json={"type": "standard", "title": "B"})
    resp = client.get("/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# B11
def test_get_task_by_id_returns_task(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Find me"}).json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


# B12
def test_get_task_by_unknown_id_returns_404(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404


# B13
def test_patch_task_performs_partial_update(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Old", "description": "Keep"}).json()
    resp = client.patch(f"/tasks/{created['id']}", json={"title": "New"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New"
    assert data["description"] == "Keep"


# B24
def test_overdue_deadline_task_can_transition_to_completed(client):
    created = client.post("/tasks/", json={"type": "deadline", "title": "Overdue but doable", "due_date": "2000-01-01T00:00:00"}).json()
    client.post(f"/tasks/{created['id']}/transition", json={"to_status": "in_progress"})
    resp = client.post(f"/tasks/{created['id']}/transition", json={"to_status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


# B23
def test_patch_deadline_task_updates_due_date(client):
    created = client.post("/tasks/", json={"type": "deadline", "title": "Reschedule me", "due_date": "2030-01-01T00:00:00"}).json()
    resp = client.patch(f"/tasks/{created['id']}", json={"due_date": "2031-12-31T00:00:00"})
    assert resp.status_code == 200
    assert resp.json()["due_date"].startswith("2031")


# B21
def test_is_overdue_true_when_due_date_in_past(client):
    created = client.post("/tasks/", json={"type": "deadline", "title": "Late task", "due_date": "2000-01-01T00:00:00"}).json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.json()["is_overdue"] is True


# B22
def test_is_overdue_false_when_due_date_in_future(client):
    created = client.post("/tasks/", json={"type": "deadline", "title": "Future task", "due_date": "2099-01-01T00:00:00"}).json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.json()["is_overdue"] is False


# B20
def test_get_deadline_task_includes_due_date_and_is_overdue(client):
    created = client.post("/tasks/", json={"type": "deadline", "title": "File taxes", "due_date": "2030-06-01T00:00:00"}).json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["due_date"] is not None
    assert data["is_overdue"] is False


# B19
def test_post_deadline_task_returns_201_with_deadline_type(client):
    resp = client.post("/tasks/", json={"type": "deadline", "title": "Submit report", "due_date": "2030-01-01T00:00:00"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "deadline"
    assert data["title"] == "Submit report"


# B14
def test_delete_task_returns_204(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Bye"}).json()
    resp = client.delete(f"/tasks/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


# B15
def test_transition_valid_move_returns_updated_task(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Start me"}).json()
    resp = client.post(f"/tasks/{created['id']}/transition", json={"to_status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


# B16
def test_transition_from_terminal_state_returns_422(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Finish me"}).json()
    client.post(f"/tasks/{created['id']}/transition", json={"to_status": "in_progress"})
    client.post(f"/tasks/{created['id']}/transition", json={"to_status": "completed"})
    resp = client.post(f"/tasks/{created['id']}/transition", json={"to_status": "pending"})
    assert resp.status_code == 422


# B17
def test_transition_disallowed_move_returns_422(client):
    created = client.post("/tasks/", json={"type": "standard", "title": "Skip"}).json()
    resp = client.post(f"/tasks/{created['id']}/transition", json={"to_status": "completed"})
    assert resp.status_code == 422


# B18
def test_transition_unknown_task_returns_404(client):
    resp = client.post("/tasks/999/transition", json={"to_status": "in_progress"})
    assert resp.status_code == 404
