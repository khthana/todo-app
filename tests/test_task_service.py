from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import StandardTask
from app.repositories.tasks import TaskRepository
from app.services.tasks import InvalidTransitionError, TaskNotFoundError, TaskService

_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
_Session = sessionmaker(bind=_engine)


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def service():
    db = _Session()
    repo = TaskRepository(db)
    yield TaskService(repo)
    db.close()


def test_get_task_raises_for_unknown_id(service):
    with pytest.raises(TaskNotFoundError):
        service.get_task(999)


def test_update_task_raises_for_unknown_id(service):
    with pytest.raises(TaskNotFoundError):
        service.update_task(999, {"title": "Ghost"})


def test_delete_task_raises_for_unknown_id(service):
    with pytest.raises(TaskNotFoundError):
        service.delete_task(999)


def test_transition_pending_to_in_progress_updates_status(service):
    task = service.create_task(title="Work item")
    updated = service.transition_task(task.id, "in_progress")
    assert updated.status == "in_progress"


def test_transition_from_terminal_state_raises(service):
    task = service.create_task(title="Done item")
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")
    with pytest.raises(InvalidTransitionError):
        service.transition_task(task.id, "pending")


def test_transition_disallowed_move_raises(service):
    task = service.create_task(title="Skip ahead")
    with pytest.raises(InvalidTransitionError):
        service.transition_task(task.id, "completed")


def test_transition_unknown_task_raises_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.transition_task(999, "in_progress")
