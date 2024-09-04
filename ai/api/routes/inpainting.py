import base64
from io import BytesIO
from typing import List

import PIL.Image
import torch
from diffusers import AutoPipelineForInpainting
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse

from api.routes.schema import ITIRequestForm

router = APIRouter(
    prefix="/inpainting",
)

@router.post("")
async def inpainting(
        request: Request
):
    form = await request.form()
    print(form)
    print(form.getlist("images"))

    model = form.get("model")
    prompt = form.get("prompt")
    negative_prompt = form.get("negative_prompt")
    num_inference_steps=int(form.get("num_inference_steps", 50))
    guidance_scale=float(form.get("guidance_scale", 7.5))
    strength=float(form.get("strength", 0.5))
    num_images_per_prompt=int(form.get("num_images_per_prompt", 1))
    batch_count=int(form.get("batch_count", 1))
    batch_size=int(form.get("batch_size", 1))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inpaint_pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16).to(device)

    images = form.getlist("images")

    init_image_list = []
    mask_image_list = []

    # PIL.Image로 변환
    for file in images:
        file_data = await file.read()
        image_bytes_io = BytesIO(file_data)
        image = PIL.Image.open(image_bytes_io)
        # 파일 이름에 붙여준 prefix에 따라 구분한 후 분리
        init_image_list.append(image) if file.filename[0] == 'i' else mask_image_list.append(image)

    # Debugging output
    print(f"Init Images: {len(init_image_list)}")
    print(f"Mask Images: {len(mask_image_list)}")

    # Ensure init and mask lists are not empty and have the correct corresponding pairs
    if not init_image_list or not mask_image_list:
        raise ValueError("Init images or mask images are missing.")

    # Ensure the number of init images matches the number of mask images
    if len(init_image_list) != len(mask_image_list):
        raise ValueError("The number of initial images and mask images must match.")

    # Generate inpainted images
    generated_image_list = inpaint_pipe(
        image=init_image_list,
        mask_image=mask_image_list,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        strength=strength,
        num_images_per_prompt=num_images_per_prompt,
    ).images


    encoded_images = []

    for image in generated_image_list:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        encoded_images.append(img_str)

    return JSONResponse(content={"image_list": encoded_images})
