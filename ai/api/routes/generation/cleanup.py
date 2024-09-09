from fastapi import APIRouter, Request, HTTPException, status
from PIL import Image
from io import BytesIO
from starlette.responses import JSONResponse
from diffusers import StableDiffusionInpaintPipeline
import os, base64, torch, numpy as np

router = APIRouter(
    prefix="/cleanup",
)

@router.post("")
async def cleanup(request: Request):
    form = await request.form()
    image = form.get("image")
    mask = form.get("mask")

    input_image = Image.open(image.file).convert("RGB")
    input_mask = Image.open(mask.file).convert("RGB")

    input_image = input_image.resize((512, 512))
    input_mask = input_mask.resize((512, 512))

    print(f"Input image size: {input_image.size}")
    print(f"Mask image size: {input_mask.size}")

    # Stable Diffusion 모델 초기화
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Inpaint 파이프라인
    inpaint_pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2", torch_dtype=torch.float16
    ).to(device)


    temp_pipe_image = inpaint_pipe(
        prompt="Seamlessly fill in the background to create a natural and coherent scene, ensuring that the area previously occupied by the removed subject blends smoothly with the surrounding environment.",
        image=input_image,
        mask_image=input_mask,
        num_inference_steps=50,
        guidance_scale=7.5
    )

    generated_image = temp_pipe_image.images[0]
    generated_image = generated_image.resize((512,512))
    # 원본 이미지와 생성된 이미지를 NumPy 배열로 변환
    init_np = np.array(input_image)
    generated_np = np.array(generated_image)
    mask_np = np.array(input_mask.convert("L"))  # 마스크 이미지를 그레이스케일로 변환

    # 마스크의 흰색 영역(255)은 생성된 이미지로, 검은색 영역(0)은 원본 이미지로 남김
    combined_np = np.where(mask_np[..., None] > 127, generated_np, init_np)

    # NumPy 배열을 다시 PIL 이미지로 변환
    final_image = Image.fromarray(combined_np.astype(np.uint8))

    buffered = BytesIO()
    final_image.save(buffered, format="PNG")
    buffered.seek(0)

    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return JSONResponse(content={"final_image": img_str})