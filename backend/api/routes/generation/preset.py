from fastapi import APIRouter, HTTPException, status, Depends
from starlette.responses import JSONResponse
from dependencies import get_current_user

from models import GenerationPreset, Member

router = APIRouter(
    prefix="/presets",
)

@router.get("")
async def get_presets(
        member: Member = Depends(get_current_user)
):
    presets = await GenerationPreset.find(GenerationPreset.member_id == member.member_id).to_list()
    return presets


@router.post("")
async def create_presets(
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