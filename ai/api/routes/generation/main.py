from fastapi import APIRouter

from api.routes.generation import cleanup_iopaint, iti, inpainting, rembg, tti

router = APIRouter(
    prefix="/generation",
    tags=["Image Generation API"]
)

router.include_router(tti.router)
router.include_router(iti.router)
router.include_router(inpainting.router)
router.include_router(rembg.router)
router.include_router(cleanup_iopaint.router)
