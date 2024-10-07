from fastapi.responses import FileResponse
from pathlib import Path
import tempfile
import shutil
from diffusers import StableDiffusionPipeline

from workers.celery import celery_app

@celery_app.task(name="download", queue="tra_queue")
def download_model(model_name, model_path):
    # 임시 디렉터리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 모델을 임시 디렉토리에 저장할 경로
        temp_model_path = Path(temp_dir) / model_name

        # 파이프라인을 통해 모델을 불러와 임시 디렉터리에 저장
        pipeline = StableDiffusionPipeline.from_pretrained(model_path)
        pipeline.save_pretrained(temp_model_path)

        # 모델을 zip 파일로 압축
        zip_file_path = shutil.make_archive(str(temp_model_path), 'zip', root_dir=str(temp_model_path))

        return zip_file_path