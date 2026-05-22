from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routers import todos
from .routers import tasks
from .services.tasks import InvalidTransitionError, TaskNotFoundError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="0.1.0")

app.include_router(todos.router)
app.include_router(tasks.router)


@app.exception_handler(TaskNotFoundError)
def task_not_found_handler(request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Task not found"})


@app.exception_handler(InvalidTransitionError)
def invalid_transition_handler(request, exc: InvalidTransitionError):
    return JSONResponse(status_code=422, content={"detail": "Invalid state transition"})


@app.get("/")
def root():
    return {"message": "Todo API is running"}
