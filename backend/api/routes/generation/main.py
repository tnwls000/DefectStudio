from fastapi import APIRouter

from api.routes.generation import tti, rembg, cleanup

router = APIRouter(
    prefix="/generation",
    tags=["generation"]
)

router.include_router(tti.router)
router.include_router(rembg.router)
router.include_router(cleanup.router)
