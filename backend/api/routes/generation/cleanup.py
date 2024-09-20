import io
import zipfile
from typing import List

import requests
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException, status
from starlette.responses import JSONResponse

from core.config import settings
from enums import GPUEnvironment
from utils.s3 import upload_files

router = APIRouter(
    prefix="/cleanup",
)

CLEAN_UP_URL = "/generation/cleanup"


@router.post("/{gpu_env}")
async def cleanup(
        gpu_env: GPUEnvironment,
        init_image_list: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
        mask_image_list: List[UploadFile] = File(..., description="업로드할 이미지 파일들의 mask 파일들"),
):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    files = []
    for image in init_image_list:
        files.append(('images', (image.filename, await image.read(), image.content_type)))
    for mask in mask_image_list:
        files.append(('masks', (mask.filename, await mask.read(), mask.content_type)))

    response = requests.post(settings.AI_SERVER_URL + CLEAN_UP_URL, files=files)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Response 데이터를 메모리 내 ZIP 파일 형태로 처리할 수 있도록 변환
    zip_file_bytes = io.BytesIO(response.content)

    # ZIP 파일에서 이미지 추출하기
    image_list = []
    with zipfile.ZipFile(zip_file_bytes) as zip_file:
        for name in zip_file.namelist():
            image_data = zip_file.read(name)
            image_stream = io.BytesIO(image_data)
            image_list.append(image_stream)

    image_url_list = upload_files(image_list, "cleanup")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"image_list": image_url_list})
