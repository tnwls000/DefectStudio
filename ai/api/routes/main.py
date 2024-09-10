from fastapi import APIRouter
from .generation import main as generation

api_router = APIRouter(
    prefix="/api"
)

api_router.include_router(generation.router)
