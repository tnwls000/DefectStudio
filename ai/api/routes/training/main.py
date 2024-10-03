import io
import json
from utils.csv import find_and_convert_csv_to_json
from celery.result import AsyncResult
from fastapi import APIRouter, status, HTTPException
from starlette.responses import JSONResponse, StreamingResponse

from api.routes.training import dreambooth
from schema import CeleryTaskResponse

router = APIRouter(
    prefix="/training",
    tags=["model Training API"]
)

router.include_router(dreambooth.router)


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = AsyncResult(task_id)

    if result.status == "PENDING":
        response = CeleryTaskResponse(
            task_status="PENDING",
            message="Task가 실행을 대기하고 있습니다."
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    elif result.status == "STARTED":
        task_arguments = result.kwargs
        output_dir = task_arguments.get("output_dir")

        # csv 파일 읽어오기
        cvs_result_in_json = find_and_convert_csv_to_json(output_dir)

        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
            message="Task가 진행중입니다.",
            result_data=json.loads(cvs_result_in_json)
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
        response = CeleryTaskResponse(
            task_name=result.name,
            task_status=result.status,
            task_arguments=result.kwargs,
            result_data=result.result
        ).model_dump(exclude_none=True)

        result.forget()
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    else:
        response = CeleryTaskResponse(
            task_status=result.status,
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)