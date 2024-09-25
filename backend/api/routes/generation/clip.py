from typing import Optional

import requests
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response, Form, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.routes.members import use_tokens
from core.config import settings
from typing import List

from dependencies import get_db, get_current_user
from enums import UseType
from models import Member
from schema.tokens import TokenUse

router = APIRouter(
    prefix="/clip"
)

CLIP_URL = "/generation/clip"

@router.post("")
async def clip(model: str = Form("ViT-L-14/openai", description="사용할 모델"),
               image_list: List[UploadFile] = File(None, description="업로드할 이미지 파일들"),
               mode: Optional[str] = Form(None, description="interrogate 모드 설정. fast/classic/negative", examples=[""]),
               caption: Optional[str] = Form(None, description="이미지 caption을 직접 설정할 경우 적는 prompt", examples=[""]),
               batch_size: Optional[int] = Form(1024, description="한 번에 처리할 수 있는 데이터의 양"),
               session: Session = Depends(get_db),
               current_user: Member = Depends(get_current_user)):

    cost = len(image_list)  # 토큰 차감 수
    # 토큰 개수 모자랄 경우 먼저 에러 처리
    if current_user.token_quantity < cost:
        raise HTTPException(status_code=400, detail="보유 토큰이 부족합니다.")

    form_data = {
        "model": model,
        "mode": mode,
        "caption": caption,
        "batch_size":batch_size
    }

    files = [('images', (image.filename, await image.read(), image.content_type)) for image in image_list]
    response = requests.post(settings.AI_SERVER_URL + CLIP_URL, files=files, data=form_data)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    prompts = response_data.get("prompts")

    # 토큰 개수 차감
    token_use = TokenUse(
        cost=cost,
        use_type=UseType.clip,
        image_quantity=cost,
        model=model
    )
    use_tokens(token_use, session, current_user)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"generated_prompts": prompts})