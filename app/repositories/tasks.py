from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def list_all(self) -> list[Task]:
        return self.db.query(Task).all()

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        self.db.delete(task)
        self.db.commit()
        return True

    def update(self, task_id: int, fields: dict) -> Task | None:
        task = self.get(task_id)
        if task is None:
            return None
        for key, value in fields.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task
