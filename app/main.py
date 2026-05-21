from fastapi import FastAPI
from .database import Base, engine
from .routers import todos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="0.1.0")

app.include_router(todos.router)


@app.get("/")
def root():
    return {"message": "Todo API is running"}
