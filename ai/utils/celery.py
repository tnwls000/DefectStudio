from celery import Celery
from core.config import settings

celery_app = Celery(
    __name__,
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.autodiscover_tasks(['utils.tasks'], force=True)

# 큐 설정
celery_app.conf.task_queues = {
    'gen_queue': {
        'exchange': 'gen_queue',
        'routing_key': 'gen_queue',
    },
    'tra_queue': {
        'exchange': 'tra_queue',
        'routing_key': 'tra_queue',
    },
}

celery_app.conf.update(
    task_serializer='pickle',           # 작업 직렬화 방법
    result_serializer='pickle',         # 결과 직렬화 방법
    accept_content=['pickle', 'json'],  # 수락할 직렬화 형식
    result_extended=True,               # 더 많은 task 정보 불러오기
    task_track_started=True,            # 작업의 status가 STARTED일 때부터 추적하기
)