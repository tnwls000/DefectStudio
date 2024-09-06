import base64
from io import BytesIO

import PIL.Image
import torch
from diffusers import AutoPipelineForInpainting
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/inpainting",
)


@router.post("")
async def inpainting(
        request: Request
):
    form = await request.form()

    model = form.get("model")
    prompt = form.get("prompt")
    negative_prompt = form.get("negative_prompt")
    num_inference_steps = int(form.get("num_inference_steps"))
    guidance_scale = float(form.get("guidance_scale"))
    strength = float(form.get("strength"))
    num_images_per_prompt = int(form.get("num_images_per_prompt"))
    init_image_files = form.getlist("init_image")
    mask_image_files = form.getlist("mask_image")
    batch_count = int(form.get("batch_count"))
    batch_size = int(form.get("batch_size"))

    init_image_list = [PIL.Image.open(BytesIO(await file.read())) for file in init_image_files]
    mask_image_list = [PIL.Image.open(BytesIO(await file.read())) for file in mask_image_files]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inpaint_pipe = AutoPipelineForInpainting.from_pretrained(model, torch_dtype=torch.float16).to(device)

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
