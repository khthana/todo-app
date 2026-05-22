from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routers import todos
from .routers import tasks
from .routers import tags
from .services.tasks import DependencyCycleError, InvalidRecurrencePatternError, InvalidTransitionError, TaskBlockedError, TaskNotFoundError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="0.1.0")

app.include_router(todos.router)
app.include_router(tasks.router)
app.include_router(tags.router)


@app.exception_handler(TaskNotFoundError)
def task_not_found_handler(request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Task not found"})


@app.exception_handler(InvalidTransitionError)
def invalid_transition_handler(request, exc: InvalidTransitionError):
    return JSONResponse(status_code=422, content={"detail": "Invalid state transition"})


@app.exception_handler(InvalidRecurrencePatternError)
def invalid_recurrence_pattern_handler(request, exc: InvalidRecurrencePatternError):
    return JSONResponse(status_code=400, content={"detail": "Invalid recurrence pattern"})


@app.exception_handler(DependencyCycleError)
def dependency_cycle_handler(request, exc: DependencyCycleError):
    return JSONResponse(status_code=400, content={"detail": "Adding this dependency would create a cycle"})


@app.exception_handler(TaskBlockedError)
def task_blocked_handler(request, exc: TaskBlockedError):
    return JSONResponse(status_code=422, content={"detail": "Task has incomplete blockers"})


@app.get("/")
def root():
    return {"message": "Todo API is running"}
