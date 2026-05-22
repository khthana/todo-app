from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base

task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("blocker_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("blocked_id", Integer, ForeignKey("tasks.id"), primary_key=True),
)

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


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

    blockers = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=lambda: Task.id == task_dependencies.c.blocked_id,
        secondaryjoin=lambda: Task.id == task_dependencies.c.blocker_id,
    )

    tags = relationship("Tag", secondary=task_tags)

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "task",
    }

    @property
    def blocker_ids(self) -> list[int]:
        return [b.id for b in self.blockers]

    @property
    def tag_names(self) -> list[str]:
        return [t.name for t in self.tags]

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
