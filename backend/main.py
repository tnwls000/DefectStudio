from fastapi import FastAPI
from celery import Celery
from redis import Redis
from rq import Queue


app = FastAPI()
redis_conn = Redis(host="localhost", port=6379)             
task_queue = Queue("task_queue", connection=redis_conn)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@celery.task
def test_function(x, y):
    import time
    time.sleep(5)
    return x / y