import io
import zipfile

import requests
from fastapi import APIRouter, status
from starlette.responses import JSONResponse

from api.routes.generation import tti, iti, inpainting, rembg, cleanup, clip, preset
from core.config import settings
from enums import SchedulerType
from utils.s3 import upload_files

router = APIRouter(
    prefix="/generation",
    tags=["generation"]
)

router.include_router(tti.router)
router.include_router(iti.router)
router.include_router(inpainting.router)
router.include_router(rembg.router)
router.include_router(cleanup.router)
router.include_router(clip.router)
router.include_router(preset.router)


@router.get("/schedulers")
def get_scheduler_list():
    return [scheduler.value for scheduler in SchedulerType]


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    response = requests.get(settings.AI_SERVER_URL + f"/generation/tasks/{task_id}")
    if response.headers['content-type'] == "application/json":
        return response.json()
    elif response.headers['content-type'] == "application/zip":
        zip_file_bytes = io.BytesIO(response.content)

        # ZIP 파일에서 이미지 추출
        image_list = []
        with zipfile.ZipFile(zip_file_bytes) as zip_file:
            for name in zip_file.namelist():
                image_data = zip_file.read(name)
                image_stream = io.BytesIO(image_data)
                image_list.append(image_stream)

        # S3에 이미지 업로드
        image_url_list = upload_files(image_list)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "SUCCESS",
                "type": "image",
                "data": image_url_list
            }
        )



