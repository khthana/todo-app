from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import RecurringTask, StandardTask
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


# --- RecurringTask Occurrence spawning ---

_BASE_DT = datetime(2026, 1, 15, 9, 0, 0)


def _make_recurring(service, pattern="DAILY", next_occ=None, end=None):
    return service.create_recurring_task(
        title="Stand-up",
        description="Daily sync",
        recurrence_pattern=pattern,
        next_occurrence=next_occ or _BASE_DT,
        end_recurrence_date=end,
    )


def test_completing_recurring_task_spawns_new_pending_occurrence(service):
    task = _make_recurring(service, pattern="DAILY")
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    occurrences = [t for t in all_tasks if isinstance(t, RecurringTask) and t.status == "pending"]
    assert len(occurrences) == 1


def test_end_of_series_no_spawn_when_next_occurrence_exceeds_end_date(service):
    end = datetime(2026, 1, 15, 8, 59, 59)  # one second before next_occurrence
    task = _make_recurring(service, pattern="DAILY", next_occ=_BASE_DT, end=end)
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    pending = [t for t in all_tasks if isinstance(t, RecurringTask) and t.status == "pending"]
    assert len(pending) == 0


def test_completing_standard_task_does_not_spawn_any_occurrence(service):
    task = service.create_task(title="One-off")
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    assert len(all_tasks) == 1


def test_end_of_series_transition_still_succeeds(service):
    end = datetime(2026, 1, 15, 8, 59, 59)
    task = _make_recurring(service, pattern="DAILY", next_occ=_BASE_DT, end=end)
    service.transition_task(task.id, "in_progress")
    completed = service.transition_task(task.id, "completed")
    assert completed.status == "completed"


def test_spawned_monthly_occurrence_next_occurrence_is_next_month(service):
    jan15 = datetime(2026, 1, 15, 9, 0, 0)
    task = _make_recurring(service, pattern="MONTHLY", next_occ=jan15)
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    spawn = next(t for t in all_tasks if isinstance(t, RecurringTask) and t.status == "pending")
    assert spawn.next_occurrence == datetime(2026, 2, 15, 9, 0, 0)


def test_spawned_weekly_occurrence_next_occurrence_is_plus_7_days(service):
    task = _make_recurring(service, pattern="WEEKLY", next_occ=_BASE_DT)
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    spawn = next(t for t in all_tasks if isinstance(t, RecurringTask) and t.status == "pending")
    assert spawn.next_occurrence == _BASE_DT + timedelta(days=7)


def test_spawned_daily_occurrence_inherits_fields_and_next_occurrence(service):
    end = datetime(2026, 12, 31)
    task = _make_recurring(service, pattern="DAILY", next_occ=_BASE_DT, end=end)
    service.transition_task(task.id, "in_progress")
    service.transition_task(task.id, "completed")

    all_tasks = service.list_tasks()
    spawn = next(t for t in all_tasks if isinstance(t, RecurringTask) and t.status == "pending")
    assert spawn.title == "Stand-up"
    assert spawn.description == "Daily sync"
    assert spawn.recurrence_pattern == "DAILY"
    assert spawn.end_recurrence_date == end
    assert spawn.next_occurrence == _BASE_DT + timedelta(days=1)
