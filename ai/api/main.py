from fastapi import APIRouter

from .routes import tti, rembg, cleanup

api_router = APIRouter(
    prefix="/api",
    tags=["Image Generation API"]
)

api_router.include_router(tti.router)
api_router.include_router(rembg.router)
api_router.include_router(cleanup.router)
