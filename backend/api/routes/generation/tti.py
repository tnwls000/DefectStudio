from fastapi import APIRouter
import requests

from api.routes.generation.schema import TTIRequest
from core.config import settings

router = APIRouter(
    prefix="/tti",
)


@router.post("")
def text_to_image(request: TTIRequest):
    payload = request.model_dump()
    response = requests.post(settings.AI_SERVER_URL + "/tti", data=payload)
    return response