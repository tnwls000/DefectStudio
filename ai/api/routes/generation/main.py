from celery.result import AsyncResult
from fastapi import APIRouter, status, HTTPException
from starlette.responses import JSONResponse, StreamingResponse
import io
from api.routes.generation import cleanup, iti, inpainting, rembg, tti, clip

router = APIRouter(
    prefix="/generation",
    tags=["Image Generation API"]
)

router.include_router(tti.router)
router.include_router(iti.router)
router.include_router(inpainting.router)
router.include_router(rembg.router)
router.include_router(cleanup.router)
router.include_router(clip.router)


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = AsyncResult(task_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task를 찾을 수 없습니다.")
    elif result.status == "PENDING":
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"status": "PENDING", "message": "Task가 실행을 대기하고 있습니다."})
    elif result.status == "STARTED":
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"status": "STARTED", "message": "Task가 진행중입니다."})
    elif result.status == "FAILURE":
        task_result = result.result
        result.forget()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "FAILURE",
                "type": type(task_result).__name__,
                "message": str(task_result)
            }
        )
    elif result.status == "SUCCESS":
        task_result = result.result
        result.forget()
        if isinstance(task_result, io.BytesIO):
            return StreamingResponse(task_result, media_type="application/zip",
                                     headers={"Content-Disposition": "attachment; filename=images.zip"})
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "SUCCESS",
                    "type": type(task_result).__name__,
                    "data": str(task_result)
                }
            )
