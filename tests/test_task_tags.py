from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories.tags import TagRepository
from app.repositories.tasks import TaskRepository
from app.services.tasks import TaskService

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
    tag_repo = TagRepository(db)
    yield TaskService(repo, tag_repo)
    db.close()


def test_list_tasks_filter_by_tag(service):
    service.create_task(title="Tagged", tags=["work"])
    service.create_task(title="Untagged")

    results = service.list_tasks(tag="work")
    assert len(results) == 1
    assert results[0].title == "Tagged"


def test_list_tasks_filter_by_status(service):
    t = service.create_task(title="Active")
    service.create_task(title="Pending only")
    service.transition_task(t.id, "in_progress")

    results = service.list_tasks(status="in_progress")
    assert len(results) == 1
    assert results[0].title == "Active"


def test_update_task_replaces_tags(service):
    task = service.create_task(title="A", tags=["old"])
    updated = service.update_task(task.id, {"tags": ["new"]})
    assert updated.tag_names == ["new"]


def test_tag_upsert_case_insensitive(service):
    service.create_task(title="A", tags=["Work"])
    service.create_task(title="B", tags=["work"])

    all_tags = service.list_tags()
    assert len(all_tags) == 1
    assert all_tags[0].name == "work"


def test_tag_upsert_idempotency_same_name_one_tag(service):
    service.create_task(title="A", tags=["work"])
    service.create_task(title="B", tags=["work"])

    all_tags = service.list_tags()
    assert len(all_tags) == 1


def test_create_task_with_tags_assigns_tag_names(service):
    task = service.create_task(title="Write docs", tags=["work", "urgent"])
    assert set(task.tag_names) == {"work", "urgent"}
