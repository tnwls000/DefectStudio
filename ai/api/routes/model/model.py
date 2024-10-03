from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse
from diffusers import StableDiffusionPipeline
import shutil
import tempfile
import os
from core.config import settings
from typing import List
from pathlib import Path

router = APIRouter(
    prefix="",
)
@router.get("/{member_id}", response_model=List[str])
async def get_model_names(member_id: str):
    member_dir = os.path.join(settings.OUTPUT_DIR, member_id)

    if not os.path.exists(member_dir):
        raise HTTPException(status_code=404, detail="해당 member에 모델이 없습니다.")

    # model_name 디렉토리 리스트 반환
    model_names = [
        name for name in os.listdir(member_dir)
        if os.path.isdir(os.path.join(member_dir, name))
    ]

    if not model_names:
        raise HTTPException(status_code=404, detail="member_id는 존재하지만, 모델이 존재하지 않습니다.")

    return model_names

@router.get("/{model_name}/download")
async def model_download(model_name: str, member_id: str):
    model_path = Path(settings.OUTPUT_DIR) / member_id / model_name
    # 모델이 존재하는지 확인
    if not model_path.exists():
        return {"error": "Model not found"}

    # 임시 디렉터리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 모델을 임시 디렉토리에 저장할 경로
        temp_model_path = Path(temp_dir) / model_name

        # 파이프라인을 통해 모델을 불러와 임시 디렉터리에 저장
        pipeline = StableDiffusionPipeline.from_pretrained(str(model_path))
        pipeline.save_pretrained(temp_model_path)

        # 모델을 zip 파일로 압축
        zip_file_path = shutil.make_archive(str(temp_model_path), 'zip', root_dir=str(temp_model_path))

        # 압축된 zip 파일을 클라이언트에 전송
        return FileResponse(path=zip_file_path, filename=f"{model_name}.zip", media_type='application/zip')