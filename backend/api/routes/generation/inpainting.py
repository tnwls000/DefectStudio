import mimetypes
import re
from pathlib import Path

import requests
from fastapi import APIRouter, status, HTTPException, Response
from starlette.responses import JSONResponse

from api.routes.generation.schema import InpaintingRequest
from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_image_files
from utils.s3 import upload_files

router = APIRouter(
    prefix="/inpainting",
)


@router.post("/{gpu_env}")
def inpainting(gpu_env: GPUEnvironment, request: InpaintingRequest):
    # TODO : 유저 인증 확인 후 토큰 사용
    payload_dict = request.model_dump()

    image_files = []
    image_input_paths = [payload_dict.get("init_input_path"), payload_dict.get("mask_input_path")]

    # image_files에 두 개의 리스트를 담는다 (초기 이미지들이 담긴 리스트, 마스킹 이미지들이 담긴 리스트)
    for i in range(2):
        image_files.append([file for file in Path(image_input_paths[i]).glob("*") if
                            re.search(r"\.(png|jpg|jpeg|jfif)$", file.suffix, re.IGNORECASE)])
        if not image_files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효한 이미지가 없습니다.")

    # 로컬 GPU 사용 시 이미지 저장 경로는 필수
    if gpu_env == GPUEnvironment.local and not payload_dict.get("output_path"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="로컬 파일 경로를 지정해주세요.")

    # 초기 이미지는 'i', 마스킹 이미지는 'm'을 파일 이름앞에 prefix로 가진다
    file_name_prefix = ['i', 'm']
    files = []

    for i in range(2):
        for image_file in image_files[i]:
            with open(image_file, "rb") as f:
                image_bytes = f.read()

                mime_type, _ = mimetypes.guess_type(image_file.name)
                if mime_type is None:
                    mime_type = "application/octet-stream"

                files.append(("images", (f"{file_name_prefix[i]}-{image_file.name}", image_bytes, mime_type)))

    response = requests.post(settings.AI_SERVER_URL + "/inpainting", files=files, data=payload_dict)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    image_list = response_data.get("image_list")

    # 로컬 GPU 사용 시 지정된 로컬 경로로 이미지 저장
    if gpu_env == GPUEnvironment.local:
        output_path = payload_dict.get("output_path")
        if save_image_files(output_path, image_list):
            return Response(status_code=status.HTTP_201_CREATED)

    # GPU 서버 사용 시 S3로 이미지 저장
    elif gpu_env == GPUEnvironment.remote:
        image_url_list = upload_files(image_list)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"image_list": image_url_list})
