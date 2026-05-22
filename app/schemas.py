from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StandardTaskCreate(BaseModel):
    type: str = "standard"
    title: str
    description: str = ""


class StandardTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskTransitionRequest(BaseModel):
    to_status: str


class TaskResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    status: str
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
