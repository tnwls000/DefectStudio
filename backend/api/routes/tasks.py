from fastapi import APIRouter, status
from starlette.responses import JSONResponse

router = APIRouter(
    prefix="/tasks",
    tags=["tasks (celery)"]
)

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    pass