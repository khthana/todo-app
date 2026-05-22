from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from .database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False, default="")
    status = Column(String(20), nullable=False, default="pending")
    due_date = Column(DateTime, nullable=True)
    reminder_time = Column(DateTime, nullable=True)
    recurrence_pattern = Column(String(20), nullable=True)
    next_occurrence = Column(DateTime, nullable=True)
    end_recurrence_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "task",
    }

    @property
    def is_overdue(self) -> bool | None:
        return None


class StandardTask(Task):
    __mapper_args__ = {
        "polymorphic_identity": "standard",
    }


class DeadlineTask(Task):
    __mapper_args__ = {
        "polymorphic_identity": "deadline",
    }

    @property
    def is_overdue(self) -> bool:
        if self.due_date is None:
            return False
        return self.due_date < datetime.utcnow()


class RecurringTask(Task):
    __mapper_args__ = {
        "polymorphic_identity": "recurring",
    }
