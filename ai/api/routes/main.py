from fastapi import APIRouter
from .generation import main as generation
from .device import main as device

api_router = APIRouter(
    prefix="/api"
)

api_router.include_router(generation.router)
api_router.include_router(device.router)
