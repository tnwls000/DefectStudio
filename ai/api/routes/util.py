from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException, status, Response
from starlette.responses import JSONResponse
import torch
import nvidia_smi

router = APIRouter(
    prefix="/device",
)


@router.get("/health")
async def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"health": "good"})


@router.get("/cuda_available")
async def cuda_available():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"cuda_available": torch.cuda.is_available()})
