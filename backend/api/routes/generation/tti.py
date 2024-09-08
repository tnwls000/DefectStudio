import json
from datetime import datetime

import requests
from fastapi import APIRouter, Response, status, HTTPException
from starlette.responses import JSONResponse

from api.routes.generation.schema import TTIRequest
from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_file_list_to_path
from utils.s3 import upload_files

router = APIRouter(
    prefix="/txt-to-img",
)


@router.post("/{gpu_env}")
def text_to_image(gpu_env: GPUEnvironment, request: TTIRequest):
    # TODO : 유저 인증 확인 후 토큰 사용

    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    payload_dict = request.model_dump()

    payload = json.dumps(payload_dict)
    response = requests.post(settings.AI_SERVER_URL + "/txt-to-img", data=payload)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    image_list = response_data.get("image_list")
    metadata = response_data.get("metadata")
    image_url_list = upload_files(image_list, "tti")

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"image_list": image_url_list, "metadata": metadata}
    )
