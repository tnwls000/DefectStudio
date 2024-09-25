import io
import zipfile
from typing import List
from typing import Optional

import requests
from fastapi import APIRouter, status, Form, UploadFile, File, HTTPException
from starlette.responses import JSONResponse

from core.config import settings
from enums import GPUEnvironment
from utils.s3 import upload_files

router = APIRouter(
    prefix="/remove-bg",
)

REMOVE_BG_URL = "/generation/remove-bg"


@router.post("/{gpu_env}")
async def remove_background(
        gpu_env: GPUEnvironment,
        model: str = Form("briaai/RMBG-1.4", description="사용할 모델"),
        batch_size: Optional[int] = Form(1, ge=1, le=10, description="한 번의 호출에서 생성할 이미지 수"),
        image_list: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
        input_path: Optional[str] = Form(None, description="이미지를 가져올 로컬 경로", examples=[""]),
        output_path: Optional[str] = Form(None, description="이미지를 저장할 로컬 경로", examples=[""])
):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    form_data = {
        "model":model,
        "batch_size":batch_size,
    }

    files = [('images', (image.filename, await image.read(), image.content_type)) for image in image_list]

    json_response = requests.post(settings.AI_SERVER_URL + REMOVE_BG_URL, files=files, data=form_data).json()
    return {"task_id": json_response.get("task_id")}