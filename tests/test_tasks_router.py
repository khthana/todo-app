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
