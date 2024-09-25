import io
import zipfile
from typing import List
from typing import Optional

import requests
from fastapi import APIRouter, status, Form, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.routes.members import use_tokens
from dependencies import get_db, get_current_user
from models import Member

from core.config import settings
from enums import GPUEnvironment, UseType
from schema.tokens import TokenUse
from utils.s3 import upload_files

router = APIRouter(
    prefix="/remove-bg",
)

REMOVE_BG_URL = "/generation/remove-bg"


@router.post("/{gpu_env}")
async def remove_background(
        gpu_env: GPUEnvironment,
        model: str = Form("briaai/RMBG-1.4", description="사용할 모델"),
        batch_size: Optional[int] = Form(1, ge=1, le=10, description="한 번에 처리할 수 있는 데이터의 양"),
        image_list: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
        input_path: Optional[str] = Form(None, description="이미지를 가져올 로컬 경로", examples=[""]),
        output_path: Optional[str] = Form(None, description="이미지를 저장할 로컬 경로", examples=[""]),
        session: Session = Depends(get_db),
        current_user: Member = Depends(get_current_user)
):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    cost = len(image_list)
    # 토큰 개수 모자랄 경우 먼저 에러 처리
    if current_user.token_quantity < cost:
        raise HTTPException(status_code=400, detail="보유 토큰이 부족합니다.")

    form_data = {
        "model":model,
        "batch_size":batch_size,
    }

    files = [('images', (image.filename, await image.read(), image.content_type)) for image in image_list]
    response = requests.post(settings.AI_SERVER_URL + REMOVE_BG_URL, files=files, data=form_data)

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

    image_url_list = upload_files(image_list)

    # 토큰 개수 차감
    token_use = TokenUse(
        cost=cost,
        use_type=UseType.remove_background,
        image_quantity=cost,
        model=model
    )
    use_tokens(token_use, session, current_user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"image_list": image_url_list}
    )
