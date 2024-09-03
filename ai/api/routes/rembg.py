import base64
from io import BytesIO
from fastapi import APIRouter, HTTPException, Request, status
from PIL import Image
from starlette.responses import JSONResponse
from transformers import pipeline

router = APIRouter(
    prefix="/remove-bg"
)

@router.post("")
async def remove_bg(request: Request):
    form = await request.form()
    images = form.getlist("images")

    if not images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미지를 첨부해주세요.")

    # 이미지 세그멘테이션 파이프라인 생성 (GPU 사용 설정)
    rmbg_pipeline = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True, device=0)

    encoded_images = []
    for image in images:
        input_image = Image.open(image.file).convert("RGBA")
        output_image = rmbg_pipeline(input_image)

        buffered = BytesIO()
        output_image.save(buffered, format="PNG")
        buffered.seek(0)

        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        encoded_images.append(img_str)

    return JSONResponse(content={"image_list": encoded_images})

