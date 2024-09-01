import json

import requests
from fastapi import APIRouter

from api.routes.generation.schema import TTIRequest
from core.config import settings

router = APIRouter(
    prefix="/tti",
)


@router.post("")
def text_to_image(request: TTIRequest):
    payload_dict = request.model_dump()
    payload = json.dumps(payload_dict)
    response = requests.post(settings.AI_SERVER_URL + "/tti", data=payload)
    # TODO : AI server API 구현 후 추가
    # images, metadata = response.json().get("images"), response.json().get("metadata")
    # for image in images:
    #     image.save(local_file_path)
    return response
