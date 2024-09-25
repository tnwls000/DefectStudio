from typing import Optional

import requests
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response, Form
from starlette.responses import JSONResponse
from core.config import settings
from typing import List

router = APIRouter(
    prefix="/clip"
)

CLIP_URL = "/generation/clip"

@router.post("")
async def clip(model: str = Form("ViT-L-14/openai", description="사용할 모델"),
               image_list: List[UploadFile] = File(None, description="업로드할 이미지 파일들"),
               mode: Optional[str] = Form(None, description="interrogate 모드 설정. fast/classic/negative", examples=[""]),
               caption: Optional[str] = Form(None, description="이미지 caption을 직접 설정할 경우 적는 prompt", examples=[""]),
               batch_size: Optional[int] = Form(1024, description="한 번에 처리할 수 있는 데이터의 양")):

    form_data = {
        "model": model,
        "mode": mode,
        "caption": caption,
        "batch_size":batch_size
    }

    files = [('images', (image.filename, await image.read(), image.content_type)) for image in image_list]

    json_response = requests.post(settings.AI_SERVER_URL + CLIP_URL, files=files, data=form_data).json()
    return {"task_id": json_response.get("task_id")}