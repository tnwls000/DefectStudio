from fastapi import APIRouter

from api.routes.generation import cleanup_iopaint, iti, inpainting, rembg, tti, clip

router = APIRouter(
    prefix="/generation",
    tags=["Image Generation API"]
)

router.include_router(tti.router)
router.include_router(iti.router)
router.include_router(inpainting.router)
router.include_router(rembg.router)
router.include_router(cleanup_iopaint.router)
router.include_router(clip.router)
