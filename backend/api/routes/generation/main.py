import io
import zipfile
from datetime import datetime
import json

import requests
from fastapi import APIRouter, status, Depends
from starlette.responses import JSONResponse

from api.routes.generation import tti, iti, inpainting, rembg, cleanup, clip, preset, log
from core.config import settings
from dependencies import get_current_user
from enums import SchedulerType
from models import Member
from schema.logs import GenerationLog, SimpleGenerationLog
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
router.include_router(log.router)


@router.get("/schedulers")
def get_scheduler_list():
    return [scheduler.value for scheduler in SchedulerType]


@router.get("/tasks/{task_id}")
async def get_task_status(
        task_id: str,
        member: Member = Depends(get_current_user)
):
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

        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d")
        formatted_time = now.strftime("%H%M%S%f")

        # S3에 이미지 업로드
        image_url_list = upload_files(image_list, formatted_date, formatted_time)

        task_name = response.headers['Task-Name']
        task_args = json.loads(response.headers['Task-Arguments'])
        print(task_args)

        log = GenerationLog(
            generation_type=task_name,
            member_id=member.member_id,
            date=now,
            num_of_generated_images=len(image_url_list),
            image_url_list=image_url_list,
            **task_args
        )

        saved_log = await log.insert()
        simple_saved_log = SimpleGenerationLog.from_orm(saved_log)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "task_name": task_name,
                "task_status": "SUCCESS",
                "result_data_type": "image",
                "result_data_log": simple_saved_log.model_dump_json()
            }
        )
