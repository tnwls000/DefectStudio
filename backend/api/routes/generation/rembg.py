import requests, re, mimetypes
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Response
from starlette.responses import JSONResponse

from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_image_files
from utils.s3 import upload_files
from typing import Optional

router = APIRouter(
    prefix="/remove-bg",
)

REMOVE_BG_URL = "/remove-bg"

@router.post("/{gpu_env}")
async def remove_background(gpu_env: GPUEnvironment,
                            input_path: str,
                            output_path: Optional[str] = None
                            ):
    # TODO: 로그인 유저 확인

    image_files = [file for file in Path(input_path).glob("*") if re.search(r"\.(png|jpg|jpeg|jfif)$", file.suffix, re.IGNORECASE)]
    if not image_files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효한 이미지가 없습니다.")

    if gpu_env == GPUEnvironment.local and not output_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="로컬 파일 경로를 지정해주세요.")

    files = []
    for image_file in image_files:
        with open(image_file, "rb") as f:
            image_bytes = f.read()

            mime_type, _ = mimetypes.guess_type(image_file.name)
            if mime_type is None:
                mime_type = "application/octet-stream"

            files.append(("images", (image_file.name, image_bytes, mime_type)))

    response = requests.post(settings.AI_SERVER_URL + REMOVE_BG_URL, files=files)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    image_list = response_data.get("image_list")

    if gpu_env == GPUEnvironment.local:
        if save_image_files(output_path, image_list):
            return Response(status_code=status.HTTP_201_CREATED)

    elif gpu_env == GPUEnvironment.remote:
        image_url_list = upload_files(image_list)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"image_list": image_url_list})