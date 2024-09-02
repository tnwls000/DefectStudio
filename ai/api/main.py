from fastapi import APIRouter

from .routes import tti

api_router = APIRouter(
    prefix="/api",
    tags=["Image Generation API"]
)

api_router.include_router(tti.router)
