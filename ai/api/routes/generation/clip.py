from io import BytesIO

import torch.cuda
from fastapi import APIRouter, Request, HTTPException
from PIL import Image
from clip_interrogator import Interrogator, Config
from starlette.responses import JSONResponse

router = APIRouter(
    prefix="/clip"
)

@router.post("")
async def clip(request: Request):
    form = await request.form()
    image = form.get("image")

    image_bytes = await image.read()
    input_image = Image.open(BytesIO(image_bytes)).convert("RGB")

    clip_config = Config(
        clip_model_name="ViT-L-14/openai",
        cache_path="./cache",
    )

    clip_config.apply_low_vram_defaults()
    clip_interrogator = Interrogator(clip_config)

    if torch.cuda.is_available():
        clip_interrogator.clip_model = clip_interrogator.clip_model.half()
        clip_interrogator.caption_model = clip_interrogator.caption_model.half()
    else:
        raise HTTPException(status_code=400, detail="CLIP API ERROR: GPU is not available.")
    prompt = clip_interrogator.interrogate(input_image)
    return JSONResponse(content={"prompt": prompt})
