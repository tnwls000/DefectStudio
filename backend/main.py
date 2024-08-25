from fastapi import FastAPI
from celery import Celery
from redis import Redis
from rq import Queue
from api.main import api_router
from core.config import settings
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from core.db import Base, engine

app = FastAPI()

# Managing Redis queues directly with rq
redis_conn = Redis(host=settings.REDIS_HOST, port=6379)
task_queue = Queue("task_queue", connection=redis_conn)

celery = Celery(
    __name__,
    broker=f"redis://{settings.REDIS_HOST}:6379/0",
    backend=f"redis://{settings.REDIS_HOST}:6379/0"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}

@celery.task
def test_function(x, y):
    import time
    time.sleep(5)
    return x / y

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    Base.metadata.create_all(bind=engine)
