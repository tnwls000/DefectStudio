from pathlib import Path
import tempfile
import shutil
from diffusers import StableDiffusionPipeline

from workers.celery import celery_app
from core.config import settings

@celery_app.task(name="download_model", queue="tra_queue")
def download_model(model_name, model_path):
    if not Path(model_path).exists():
        return {"error": "Model not found"}

    permanent_dir = Path(settings.DOWNLOAD_TEMP_DIR)
    permanent_model_path = permanent_dir / model_name

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_model_path = Path(temp_dir) / model_name

        pipeline = StableDiffusionPipeline.from_pretrained(model_path)
        pipeline.save_pretrained(temp_model_path)

        zip_file_path = shutil.make_archive(str(permanent_model_path), 'zip', root_dir=str(temp_model_path))

        return zip_file_path