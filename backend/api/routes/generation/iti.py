from io import BytesIO
import PIL

import requests
from fastapi import APIRouter, status, HTTPException, Request, Response, Form, UploadFile, File
from typing import Optional, List
from starlette.responses import JSONResponse
from pydantic import ValidationError

from api.routes.generation.schema import ITIRequest
from core.config import settings
from enums import GPUEnvironment
from utils.local_io import save_file_list_to_path
from utils.s3 import upload_files

router = APIRouter(
    prefix="/img-to-img",
)


@router.post("/{gpu_env}")
async def image_to_image(
        gpu_env: GPUEnvironment,
        model: str = Form("CompVis/stable-diffusion-v1-4"),
        prompt: str = Form(..., description="이미지를 생성할 텍스트 프롬프트"),
        negative_prompt: Optional[str] = Form(None),
        num_inference_steps: Optional[int] = Form(50),
        guidance_scale: Optional[float] = Form(7.5),
        strength: Optional[float] = Form(0.5),
        num_images_per_prompt: Optional[int] = Form(1),
        batch_count: Optional[int] = Form(1),
        batch_size: Optional[int] = Form(1),
        images: List[UploadFile] = File(...),  # 이미지 파일
        input_path: Optional[str] = Form(None, description="이미지를 가져올 로컬 경로"),
        output_path: Optional[str] = Form(None, description="이미지를 저장할 로컬 경로")
):

    # TODO : 유저 인증 확인 후 토큰 사용
    form_data = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "strength": strength,
        "num_images_per_prompt": num_images_per_prompt,
        "batch_count": batch_count,
        "batch_size": batch_size,
    }

    try:
        validated_form_data= ITIRequest(**form_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    files = []
    for file in images:
        file_data = await file.read()
        image_bytes_io = BytesIO(file_data)
        image_bytes_io.seek(0)
        files.append(('images', (file.filename, image_bytes_io, file.content_type)))

    response = requests.post(settings.AI_SERVER_URL + "/img-to-img", files=files, data=validated_form_data.model_dump())

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    image_list = response_data.get("image_list")

    # 로컬 GPU 사용 시 지정된 로컬 경로로 이미지 저장
    if gpu_env == GPUEnvironment.local:
        if save_file_list_to_path(output_path, image_list):
            return Response(status_code=status.HTTP_201_CREATED)

    # GPU 서버 사용 시 S3로 이미지 저장
    elif gpu_env == GPUEnvironment.remote:
        image_url_list = upload_files(image_list)
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content={"image_list": image_url_list})
