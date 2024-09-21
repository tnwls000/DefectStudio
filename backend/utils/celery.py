from fastapi import HTTPException, status
import io
import zipfile
from celery import Celery
import requests
from core.config import settings
from utils.s3 import upload_files
from starlette.responses import JSONResponse

celery = Celery(
    __name__,
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# 큐 설정
celery.conf.task_queues = {
    'gen_queue': {
        'exchange': 'gen_queue',
        'routing_key': 'gen_queue',
    },
    'tra_queue': {
        'exchange': 'tra_queue',
        'routing_key': 'tra_queue',
    },
}

celery.conf.update(
    task_serializer='json',  # 작업 직렬화 방법
    result_serializer='json',  # 결과 직렬화 방법
    accept_content=['json'],  # 수락할 직렬화 형식
)

# AI 서버로 Generation 요청을 보내는 Celery Task
@celery.task(name="generate", queue="gen_queue")
def generate_task(url, **kwargs):
    try:
        response = requests.post(url, **kwargs)
        response.raise_for_status()

        # Response 데이터를 메모리 내 ZIP 파일 형태로 처리할 수 있도록 변환
        zip_file_bytes = io.BytesIO(response.content)

        # ZIP 파일 이름 추출
        content_disposition = response.headers.get('Content-Disposition')
        zipfile_name = content_disposition.split('filename=')[1].strip('\"')

        # ZIP 파일에서 이미지 추출하기
        image_list = []
        with zipfile.ZipFile(zip_file_bytes) as zip_file:
            for name in zip_file.namelist():
                image_data = zip_file.read(name)
                image_stream = io.BytesIO(image_data)
                image_list.append(image_stream)

        image_url_list = upload_files(image_list, zipfile_name)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"image_list": image_url_list}
        )
    except HTTPException as e:
        return {"status_code": 500, "detail": str(e)}