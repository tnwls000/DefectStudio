import requests
from typing import Optional
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException, status, Response
from starlette.responses import JSONResponse
from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_file_list_to_path
from utils.s3 import upload_files
from typing import List

router = APIRouter(
    prefix="/cleanup",
)

CLEAN_UP_URL = "/cleanup"


@router.post("/{gpu_env}")
async def cleanup(gpu_env: GPUEnvironment,
                  image: UploadFile = File(...),
                  mask: UploadFile = File(...),
                  output_path: Optional[str] = None):
    # TODO: 로그인 유저 확인

    if gpu_env == GPUEnvironment.local and not output_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="로컬 파일 경로를 지정해주세요.")

    files = {
        'image': (image.filename, await image.read(), image.content_type),
        'mask': (mask.filename, await mask.read(), mask.content_type),
    }

    response = requests.post(settings.AI_SERVER_URL+CLEAN_UP_URL, files=files)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    final_image = response_data.get("final_image")
    image_list = [final_image]

    if gpu_env == GPUEnvironment.local:
        if save_file_list_to_path(output_path, image_list):
            return Response(status_code=status.HTTP_201_CREATED)

    elif gpu_env == GPUEnvironment.remote:
        image_url_list = upload_files(image_list)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"image_list": image_url_list})
