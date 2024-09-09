from contextlib import asynccontextmanager

import uvicorn
from rq import Queue
from redis import Redis
from celery import Celery
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from models import *
from core.db import engine
from api.main import api_router
from core.config import settings
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import expire_tokens

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(expire_tokens, 'cron', hour=0, minute=0)
    scheduler.start()
    Base.metadata.create_all(bind=engine)
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# Managing Redis queues directly with rq
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
task_queue = Queue("task_queue", connection=redis_conn)

celery = Celery(
    __name__,
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization", "Content-Length", "Set-Cookie"],
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
