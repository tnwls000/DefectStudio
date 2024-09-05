from typing import List
from typing import Optional

import requests
from fastapi import APIRouter, status, Response, Form, UploadFile, File, HTTPException
from starlette.responses import JSONResponse

from core.config import settings
from enums import GPUEnvironment
from utils.s3 import upload_files

router = APIRouter(
    prefix="/remove-bg",
)

REMOVE_BG_URL = "/remove-bg"


@router.post("/{gpu_env}")
async def remove_background(
        gpu_env: GPUEnvironment,
        images: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
        input_path: Optional[str] = Form(None, description="이미지를 가져올 로컬 경로"),
        output_path: Optional[str] = Form(None, description="이미지를 저장할 로컬 경로")
):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    # TODO: 로그인 유저 확인

    files = [('images', (image.filename, await image.read(), image.content_type)) for image in images]
    response = requests.post(settings.AI_SERVER_URL + REMOVE_BG_URL, files=files)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    image_list = response_data.get("image_list")
    image_url_list = upload_files(image_list)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"image_list": image_url_list})
