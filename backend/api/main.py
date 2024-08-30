from fastapi import APIRouter
from .routes import auth, members, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(members.router)
api_router.include_router(admin.router)