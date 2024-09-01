from fastapi import APIRouter
from .routes import tti

api_router = APIRouter()

api_router.include_router(tti.router)
