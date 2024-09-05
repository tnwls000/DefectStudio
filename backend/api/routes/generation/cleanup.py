from typing import Optional

import requests
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException, status, Response
from starlette.responses import JSONResponse

from core.config import settings
from enums import GPUEnvironment
from utils.s3 import upload_files

router = APIRouter(
    prefix="/cleanup",
)

CLEAN_UP_URL = "/cleanup"


@router.post("/{gpu_env}")
async def cleanup(
        gpu_env: GPUEnvironment,
        image: UploadFile = File(...),
        mask: UploadFile = File(...),
        output_path: Optional[str] = None
):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    # TODO: 로그인 유저 확인

    files = {
        'image': (image.filename, await image.read(), image.content_type),
        'mask': (mask.filename, await mask.read(), mask.content_type),
    }

    response = requests.post(settings.AI_SERVER_URL + CLEAN_UP_URL, files=files)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    final_image = response_data.get("final_image")
    image_list = [final_image]
    image_url_list = upload_files(image_list)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"image_list": image_url_list})
