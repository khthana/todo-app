from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import StandardTask
from app.repositories.tasks import TaskRepository

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
_Session = sessionmaker(bind=_engine)


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def repo():
    db = _Session()
    yield TaskRepository(db)
    db.close()


def test_create_standard_task_persists_and_returns_id(repo):
    task = repo.create(StandardTask(title="Write tests", description="Use TDD"))
    assert task.id is not None
    assert task.title == "Write tests"
    assert task.type == "standard"


def test_get_returns_task_by_id(repo):
    created = repo.create(StandardTask(title="Find me"))
    found = repo.get(created.id)
    assert found is not None
    assert found.id == created.id


def test_get_returns_none_for_unknown_id(repo):
    assert repo.get(999) is None


def test_list_all_returns_all_created_tasks(repo):
    repo.create(StandardTask(title="Task A"))
    repo.create(StandardTask(title="Task B"))
    tasks = repo.list_all()
    assert len(tasks) == 2


def test_update_changes_supplied_fields_only(repo):
    task = repo.create(StandardTask(title="Original", description="Keep me"))
    updated = repo.update(task.id, {"title": "Changed"})
    assert updated.title == "Changed"
    assert updated.description == "Keep me"


def test_delete_removes_task(repo):
    task = repo.create(StandardTask(title="Doomed"))
    repo.delete(task.id)
    assert repo.get(task.id) is None
