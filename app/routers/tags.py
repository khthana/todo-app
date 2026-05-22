from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..repositories.tags import TagRepository
from ..repositories.tasks import TaskRepository
from ..services.tasks import TaskService

router = APIRouter(prefix="/tags", tags=["tags"])


def _service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), TagRepository(db))


@router.get("/", response_model=list[schemas.TagResponse])
def list_tags(svc: TaskService = Depends(_service)):
    return svc.list_tags()
