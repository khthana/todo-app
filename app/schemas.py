from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class StandardTaskCreate(BaseModel):
    type: Literal["standard"] = "standard"
    title: str
    description: str = ""
    tags: list[str] = []


class DeadlineTaskCreate(BaseModel):
    type: Literal["deadline"] = "deadline"
    title: str
    description: str = ""
    due_date: datetime
    reminder_time: datetime | None = None
    tags: list[str] = []


class RecurringTaskCreate(BaseModel):
    type: Literal["recurring"] = "recurring"
    title: str
    description: str = ""
    recurrence_pattern: str
    next_occurrence: datetime
    end_recurrence_date: datetime | None = None
    tags: list[str] = []


TaskCreate = Annotated[Union[StandardTaskCreate, DeadlineTaskCreate, RecurringTaskCreate], Field(discriminator="type")]


class StandardTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    tags: list[str] | None = None


class TaskTransitionRequest(BaseModel):
    to_status: str


class DependencyRequest(BaseModel):
    blocker_id: int


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    status: str
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    is_overdue: bool | None = None
    recurrence_pattern: str | None = None
    next_occurrence: datetime | None = None
    end_recurrence_date: datetime | None = None
    blocker_ids: list[int] = []
    tag_names: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodoBase(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(TodoBase):
    id: int

    model_config = {"from_attributes": True}
