from pydantic import BaseModel


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
