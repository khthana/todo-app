from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..repositories.tags import TagRepository
from ..repositories.tasks import TaskRepository
from ..services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), TagRepository(db))


@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(payload: schemas.TaskCreate, svc: TaskService = Depends(_service)):
    if isinstance(payload, schemas.DeadlineTaskCreate):
        return svc.create_deadline_task(
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            reminder_time=payload.reminder_time,
            tags=payload.tags,
        )
    if isinstance(payload, schemas.RecurringTaskCreate):
        return svc.create_recurring_task(
            title=payload.title,
            description=payload.description,
            recurrence_pattern=payload.recurrence_pattern,
            next_occurrence=payload.next_occurrence,
            end_recurrence_date=payload.end_recurrence_date,
            tags=payload.tags,
        )
    return svc.create_task(title=payload.title, description=payload.description, tags=payload.tags)


@router.get("/", response_model=list[schemas.TaskResponse])
def list_tasks(
    status: str | None = None,
    tag: str | None = None,
    svc: TaskService = Depends(_service),
):
    return svc.list_tasks(status=status, tag=tag)


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, svc: TaskService = Depends(_service)):
    return svc.get_task(task_id)


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, payload: schemas.TaskUpdate, svc: TaskService = Depends(_service)):
    fields = payload.model_dump(exclude_unset=True)
    return svc.update_task(task_id, fields)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, svc: TaskService = Depends(_service)):
    svc.delete_task(task_id)


@router.post("/{task_id}/transition", response_model=schemas.TaskResponse)
def transition_task(task_id: int, payload: schemas.TaskTransitionRequest, svc: TaskService = Depends(_service)):
    return svc.transition_task(task_id, payload.to_status)


@router.post("/{task_id}/dependencies", response_model=schemas.TaskResponse)
def add_dependency(task_id: int, payload: schemas.DependencyRequest, svc: TaskService = Depends(_service)):
    return svc.add_dependency(task_id, payload.blocker_id)


@router.delete("/{task_id}/dependencies/{blocker_id}", response_model=schemas.TaskResponse)
def remove_dependency(task_id: int, blocker_id: int, svc: TaskService = Depends(_service)):
    return svc.remove_dependency(task_id, blocker_id)
