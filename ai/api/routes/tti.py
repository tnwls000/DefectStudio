import base64
import random
from io import BytesIO

import torch
from diffusers import StableDiffusionPipeline
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/txt-to-img",
)

@router.post("")
async def text_to_image(request: Request):
    form = await request.form()
    print(form)

    model = form.get("model")
    prompt = form.get("prompt")
    negative_prompt = form.get("negative_prompt")
    width = int(form.get("width"))
    height = int(form.get("height"))
    num_inference_steps = int(form.get("num_inference_steps"))
    guidance_scale = float(form.get("guidance_scale"))
    seed = int(form.get("seed"))
    batch_count = int(form.get("batch_count"))
    batch_size = int(form.get("batch_size"))
    num_images_per_prompt = int(form.get("num_images_per_prompt"))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t2i_pipe = StableDiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16).to(device)

    if seed == -1:
        seed = random.randint(0, 2 ** 32 - 1)

    image_list = []
    metadata = []

    total_images = batch_size * batch_count
    seeds = [seed + i for i in range(total_images)]

    # 각 배치의 이미지 생성
    for i in range(batch_count):
        # 현재 배치에 사용될 시드 설정
        current_seeds = seeds[i * batch_size: (i + 1) * batch_size]

        # 생성할 이미지 개수만큼의 랜덤 생성기를 미리 준비
        generators = [torch.Generator(device=device).manual_seed(s) for s in current_seeds]

        images = t2i_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generators,
            num_images_per_prompt=num_images_per_prompt
        ).images

        image_list.extend(images)

        for j in range(batch_size):
            metadata.append({
                'batch': i,
                'image_index': j,
                'seed': current_seeds[j],
                'num_inference_steps': num_inference_steps,
                'guidance_scale': guidance_scale,
                'prompt': prompt
            })

    encoded_images = []

    # 바이트 형식의 이미지를 JSON 직렬화 가능하게 만들기 위해 base64 인코딩
    for image in image_list:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        encoded_images.append(img_str)

    return JSONResponse(content={"image_list": encoded_images, "metadata": metadata})
