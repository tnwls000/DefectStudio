import json

import requests
from fastapi import APIRouter, Response, status, HTTPException
from starlette.responses import JSONResponse

from api.routes.generation.schema import TTIRequest
from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_image_files
from utils.s3 import upload_files

router = APIRouter(
    prefix="/tti",
)


@router.post("/{gpu_env}")
def text_to_image(gpu_env: GPUEnvironment, request: TTIRequest):
    # TODO : 유저 인증 확인 후 토큰 사용
    payload_dict = request.model_dump()

    # 로컬 GPU 사용 시 이미지 저장 경로는 필수
    if gpu_env == GPUEnvironment.local and not payload_dict.get("output_path"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="로컬 파일 경로를 지정해주세요.")

    payload = json.dumps(payload_dict)
    response = requests.post(settings.AI_SERVER_URL + "/tti", data=payload)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    image_list = response_data.get("image_list")
    metadata = response_data.get("metadata")

    # 로컬 GPU 사용 시 지정된 로컬 경로로 이미지 저장
    if gpu_env == GPUEnvironment.local:
        # r"C:\Users\SSAFY\Desktop"
        output_path = payload_dict.get("output_path")
        print(output_path)

        if save_image_files(output_path, image_list):
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=metadata)

    # GPU 서버 사용 시 S3로 이미지 저장
    elif gpu_env == GPUEnvironment.remote:
        image_url_list = upload_files(image_list)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"image_list": image_url_list, "metadata": metadata})
