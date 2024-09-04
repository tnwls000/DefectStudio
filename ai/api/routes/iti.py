import base64
import os
from io import BytesIO
from typing import List

import PIL.Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse

from api.routes.schema import ITIRequestForm

router = APIRouter(
    prefix="/img-to-img",
)

# os.environ["CUDA_VISIBLE_DEVICES"]="1"

@router.post("")
async def image_to_image(
        request: Request
):
    form = await request.form()
    print(form)

    model=form.get("model", "CompVis/stable-diffusion-v1-4")
    prompt=form.get("prompt")
    negative_prompt=form.get("negative_prompt")
    num_inference_steps=int(form.get("num_inference_steps", 50))
    guidance_scale=float(form.get("guidance_scale", 7.5))
    strength=float(form.get("strength", 0.5))
    num_images_per_prompt=int(form.get("num_images_per_prompt", 1))
    batch_count=int(form.get("batch_count", 1))
    batch_size=int(form.get("batch_size", 1))

    # 파일 추출
    images = form.getlist("images")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    i2i_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model, torch_dtype=torch.float16).to(device)

    image_list = []

    # PIL.Image로 변환
    for file in images:
        file_data = await file.read()
        image_bytes_io = BytesIO(file_data)
        image = PIL.Image.open(image_bytes_io)
        image_list.append(image)

    generated_image_list = i2i_pipe(
        image=image_list,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        strength=strength,
        num_images_per_prompt=num_images_per_prompt,
    ).images

    encoded_images = []

    for image in generated_image_list:
        image_bytes_io = BytesIO()
        image.save(image_bytes_io, format="PNG")
        img_str = base64.b64encode(image_bytes_io.getvalue()).decode("utf-8")
        encoded_images.append(img_str)

    return JSONResponse(content={"image_list": encoded_images})
