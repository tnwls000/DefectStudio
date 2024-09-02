from fastapi import APIRouter

from api.routes.generation import tti

router = APIRouter(
    prefix="/generation",
    tags=["generation"]
)

router.include_router(tti.router)
