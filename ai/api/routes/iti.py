import base64
from io import BytesIO

import PIL.Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/img-to-img",
)


@router.post("")
async def image_to_image(
        request: Request
):
    form = await request.form()

    model = form.get("model", "CompVis/stable-diffusion-v1-4")
    prompt = form.get("prompt")
    negative_prompt = form.get("negative_prompt")
    num_inference_steps = int(form.get("num_inference_steps"))
    guidance_scale = float(form.get("guidance_scale"))
    strength = float(form.get("strength"))
    num_images_per_prompt = int(form.get("num_images_per_prompt"))
    batch_count = int(form.get("batch_count"))
    batch_size = int(form.get("batch_size"))

    images = form.getlist("images")
    image_list = [PIL.Image.open(BytesIO(await file.read())) for file in images]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    i2i_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model, torch_dtype=torch.float16).to(device)

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
