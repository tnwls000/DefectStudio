from fastapi import APIRouter, status
from utils import celery
from starlette.responses import JSONResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks (celery)"]
)

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = celery.AsyncResult(task_id)
    if task.state == "PENDING":
        return JSONResponse(status_code=status.HTTP_200_OK, content="작업이 진행중입니다.")
    return task.info