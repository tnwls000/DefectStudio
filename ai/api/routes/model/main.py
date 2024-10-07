import io
import json
from utils.csv import find_and_convert_csv_to_json
from celery.result import AsyncResult
from fastapi import APIRouter, status, HTTPException
from starlette.responses import JSONResponse, StreamingResponse
from pathlib import Path
from schema import CeleryTaskResponse
from api.routes.model import model

router = APIRouter(
    prefix="/model",
    tags=["GPU Server Model Related API"]
)

router.include_router(model.router)

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
            result_data=cvs_result_in_json
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
        if isinstance(result.result, str) and result.result.endswith(".zip"):
            task_result = result.result
            task_name = result.name
            task_arguments = result.kwargs

            # 압축된 zip 파일 경로에서 파일 내용을 읽어 스트리밍
            with open(task_result, "rb") as file:
                zip_file = io.BytesIO(file.read())

            # 파일명을 설정
            zip_filename = f"{Path(task_result).stem}.zip"  # 파일명 추출

            result.forget()
            return StreamingResponse(zip_file, media_type="application/zip",
                                     headers={
                                         "Content-Disposition": f"attachment; filename={zip_filename}",
                                         "Task-Name": task_name,
                                         "Task-Arguments": json.dumps(task_arguments),
                                     })
    else:
        response = CeleryTaskResponse(
            task_status=result.status,
        ).model_dump(exclude_none=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)
