from fastapi import APIRouter

app = APIRouter(
    prefix="/members",
    tags=["members"]
)