from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories.tasks import TaskRepository
from app.services.tasks import (
    DependencyCycleError,
    TaskBlockedError,
    TaskService,
)

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


def _task(service, title="Task"):
    return service.create_task(title=title)


def test_cancelled_blocker_still_blocks_completion(service):
    blocker = _task(service, "Cancelled blocker")
    task = _task(service, "Dependent")
    service.add_dependency(task.id, blocker.id)

    service.transition_task(blocker.id, "cancelled")
    service.transition_task(task.id, "in_progress")
    with pytest.raises(TaskBlockedError):
        service.transition_task(task.id, "completed")


def test_remove_dependency_unblocks_task(service):
    blocker = _task(service, "Was blocking")
    task = _task(service, "Dependent")
    service.add_dependency(task.id, blocker.id)

    updated = service.remove_dependency(task.id, blocker.id)

    assert len(updated.blockers) == 0


def test_all_blockers_completed_allows_transition(service):
    blocker = _task(service, "Prerequisite")
    task = _task(service, "Dependent")
    service.add_dependency(task.id, blocker.id)

    service.transition_task(blocker.id, "in_progress")
    service.transition_task(blocker.id, "completed")
    service.transition_task(task.id, "in_progress")
    result = service.transition_task(task.id, "completed")

    assert result.status == "completed"


def test_completing_task_with_pending_blocker_raises_task_blocked(service):
    blocker = _task(service, "Blocker")
    task = _task(service, "Dependent")
    service.add_dependency(task.id, blocker.id)

    service.transition_task(task.id, "in_progress")
    with pytest.raises(TaskBlockedError):
        service.transition_task(task.id, "completed")


def test_multihop_cycle_raises_dependency_cycle_error(service):
    a = _task(service, "A")
    b = _task(service, "B")
    c = _task(service, "C")
    service.add_dependency(b.id, a.id)  # A→B
    service.add_dependency(c.id, b.id)  # B→C

    with pytest.raises(DependencyCycleError):
        service.add_dependency(a.id, c.id)  # C→A → cycle A→B→C→A


def test_direct_cycle_raises_dependency_cycle_error(service):
    a = _task(service, "A")
    b = _task(service, "B")
    service.add_dependency(b.id, a.id)  # A blocks B

    with pytest.raises(DependencyCycleError):
        service.add_dependency(a.id, b.id)  # B blocks A → cycle


def test_add_dependency_gives_task_one_blocker(service):
    task = _task(service, "Write tests")
    blocker = _task(service, "Setup env")

    updated = service.add_dependency(task.id, blocker.id)

    assert len(updated.blockers) == 1
    assert updated.blockers[0].id == blocker.id
