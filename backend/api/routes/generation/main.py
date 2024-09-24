import io
import pickle
import zipfile

from aioredis import Redis
from fastapi import APIRouter, status, HTTPException, Depends
from starlette.responses import JSONResponse

from api.routes.generation import tti, iti, inpainting, rembg, cleanup, clip, preset
from dependencies import get_redis
from enums import SchedulerType
from utils.s3 import upload_files

router = APIRouter(
    prefix="/generation",
    tags=["generation"]
)

router.include_router(tti.router)
router.include_router(iti.router)
router.include_router(inpainting.router)
router.include_router(rembg.router)
router.include_router(cleanup.router)
router.include_router(clip.router)
router.include_router(preset.router)


@router.get("/schedulers")
def get_scheduler_list():
    return [scheduler.value for scheduler in SchedulerType]


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, redis: Redis = Depends(get_redis)):
    task_key = f'celery-task-meta-{task_id}'
    raw_task_result = await redis.get(task_key)

    if not raw_task_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task를 찾을 수 없습니다.")

    task_result = pickle.loads(raw_task_result)

    if task_result.get("status") == "PENDING":
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"status": task_result.get("status"), "message": "Task가 실행을 대기하고 있습니다."})
    elif task_result.get("status") == "STARTED":
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"status": task_result.get("status"), "message": "Task가 진행중입니다."})
    elif task_result.get("status") == "FAILURE":
        error = task_result.get("result")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": task_result.get("status"),
                "error": type(error).__name__,
                "message": f"AI 서버 에러: {error}"
            }
        )
    elif task_result.get("status") == "SUCCESS":
        if type(task_result.get("result")) == bytes:
            # Task 결과로 바이너리 데이터가 반환되면 S3에 이미지가 업로드 되지 않은 상태이므로 업로드함
            zip_file_bytes = io.BytesIO(task_result.get("result"))

            # ZIP 파일에서 이미지 추출
            image_list = []
            with zipfile.ZipFile(zip_file_bytes) as zip_file:
                for name in zip_file.namelist():
                    image_data = zip_file.read(name)
                    image_stream = io.BytesIO(image_data)
                    image_list.append(image_stream)

            # S3에 이미지 업로드
            image_url_list = upload_files(image_list)

            # 업로드 완료된 이미지들의 URL 리스트를 Task Result에 저장
            task_result["result"] = image_url_list
            await redis.set(task_key, pickle.dumps(task_result))
        else:
            # 동일한 Task ID로 다시 조회하면 URL 리스트를 결과로 받을 수 있음
            image_url_list = task_result.get("result")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": task_result.get("status"),
                "message": "Task가 완료되었습니다.",
                "processed_data": image_url_list
            }
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": task_result.get("status")})
