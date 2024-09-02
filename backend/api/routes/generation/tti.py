import json
import os
import base64

import requests
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

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

    if response.status_code == 200:
        response_data = response.json()

        image_list = response_data.get("image_list")
        metadata = response_data.get("metadata")

        user_path = r"C:\Users\SSAFY\Desktop"
        os.makedirs(user_path, exist_ok=True)

        try:
            for index, image_data in enumerate(image_list):
                image_bytes = base64.b64decode(image_data)
                image_filename = os.path.join(user_path, f"{index}.jpg")
                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)
            return Response(status_code=201, content=metadata)

        except Exception as e:
            print(e)
            return Response(status_code=500, content="파일 생성에 실패하였습니다.")

    else:
        return Response(status_code=response.status_code, content=response.content)

