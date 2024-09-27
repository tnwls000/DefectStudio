import io
import json

from celery.result import AsyncResult
from fastapi import APIRouter, status, HTTPException
from starlette.responses import JSONResponse, StreamingResponse

from api.routes.generation import cleanup, iti, inpainting, rembg, tti, clip
from schema import CeleryTaskResponse

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

    if not result.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task를 찾을 수 없습니다.")

    elif result.status == "PENDING":
        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
            message="Task가 실행을 대기하고 있습니다."
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    elif result.status == "STARTED":
        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
            message="Task가 진행중입니다."
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    elif result.status == "FAILURE":
        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
            result_data_type=type(result.result).__name__,
            result_data=str(result.result)
        ).model_dump(exclude_none=True)

        result.forget()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response)

    elif result.status == "SUCCESS":
        # 결과가 Image(ZIP FILE)일 때
        if isinstance(result.result, io.BytesIO):
            task_result = result.result
            task_name = result.name
            task_arguments = result.kwargs

            result.forget()
            return StreamingResponse(task_result, media_type="application/zip",
                                     # 필요한 정보는 헤더에 넣어줘서 응답
                                     headers={
                                         "Content-Disposition": "attachment; filename=images.zip",
                                         "Task-Name": task_name,
                                         "Task-Arguments": json.dumps(task_arguments),
                                     })
        # 결과가 Json Serializable한 객체일 때
        else:
            response = CeleryTaskResponse(
                task_name=result.name,
                task_status=result.status,
                task_arguments=result.kwargs,
                result_data_type=type(result.result).__name__,
                result_data=result.result
            ).model_dump(exclude_none=True)

            result.forget()
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
    else:
        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)
