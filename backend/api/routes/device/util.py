import requests
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Response
from starlette.responses import JSONResponse
from core.config import settings
from enums import GPUEnvironment

router = APIRouter(
    prefix="/device",
)

# GPU 상태 확인 API (Health, CUDA Available, CUDA Usage)

@router.get("/health")
async def health():
    response = requests.get(f"{settings.AI_SERVER_URL}/device/health")

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response_data})

@router.get("/cuda_available")
async def cuda_available():
    response = requests.get(f"{settings.AI_SERVER_URL}/device/cuda_available")

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response_data})


