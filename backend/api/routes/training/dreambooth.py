from fastapi import APIRouter

router = APIRouter(
    prefix="/dreambooth",
)

@router.post("/{gpu_env}")
def dreambooth(gpu_env: GPUEnvironment):


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"content": "학습 요청 성공"}
    )