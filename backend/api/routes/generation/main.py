from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from api.routes.generation import tti, iti, inpainting, rembg, cleanup, clip
from dependencies import get_current_user
from enums import SchedulerType
from models import GenerationPreset, Member

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


@router.get("/schedulers")
def get_scheduler_list():
    return [scheduler.value for scheduler in SchedulerType]


@router.post("/presets")
async def save_presets(
        request: GenerationPreset,
        member: Member = Depends(get_current_user)
):
    all_none = all(
        getattr(request, field) is None
        for field in request.model_dump(exclude={"preset_title", "generation_type", "member_id", "date"})
    )

    if all_none:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 하나의 파라미터를 입력해야 합니다."
        )

    request.member_id = member.member_id

    data = await request.insert()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=data.json())
