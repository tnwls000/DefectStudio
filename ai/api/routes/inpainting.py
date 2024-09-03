import base64
from io import BytesIO
from typing import List

import PIL.Image
import torch
from diffusers import AutoPipelineForInpainting
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse

from schema import ITIRequestForm

router = APIRouter(
    prefix="/img-to-img",
)

@router.post("")
async def image_to_image(
        request: Request,
        files: List[UploadFile] = File(...),
        form_data: ITIRequestForm = Form(...)
):
    request_body = await request.json()

    model = request_body.get("model")
    prompt = request_body.get("prompt")
    negative_prompt = request_body.get("negative_prompt")
    num_inference_steps = request_body.get("num_inference_steps")
    guidance_scale = request_body.get("guidance_scale")
    strength = request_body.get("strength")
    num_images_per_prompt = request_body.get("num_images_per_prompt")
    batch_count = request_body.get("batch_count")
    batch_size = request_body.get("batch_size")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inpaint_pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16).to(device)

    init_image_list = []
    mask_image_list = []

    for field_name, (file_name, file_data, mime_type) in files:
        if field_name == "images":
            image_bytes_io = BytesIO(file_data)
            image = PIL.Image.open(image_bytes_io)
            # 파일 이름에 붙여준 prefix에 따라 구분한 후 분리
            init_image_list.append(image) if file_name[0] == 'i' else mask_image_list.append(image)

    generated_image_list = inpaint_pipe(
        image=init_image_list,
        mask_image_list=mask_image_list,
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
