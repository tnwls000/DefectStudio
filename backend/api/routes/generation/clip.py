import requests
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response
from starlette.responses import JSONResponse
from core.config import settings
from utils.s3 import upload_files

router = APIRouter(
    prefix="/clip"
)

CLIP_URL = "/generation/clip"

@router.post("")
async def clip(image: UploadFile = File(...)):

    # TODO: 로그인 유저 확인

    files = {
        "image": (image.filename, await image.read(), image.content_type)
    }

    response = requests.post(settings.AI_SERVER_URL + CLIP_URL, files=files)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()

    prompt = response_data.get("prompt")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"generated_prompt": prompt})