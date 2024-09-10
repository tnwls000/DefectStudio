from fastapi import APIRouter, Request, HTTPException, status
from PIL import Image
from io import BytesIO
from starlette.responses import JSONResponse
import subprocess, os, base64

router = APIRouter(
    prefix="/cleanup",
)

@router.post("")
async def cleanup(request: Request):
    form = await request.form()
    image = form.get("image")
    mask = form.get("mask")

    input_image = Image.open(image.file).convert("RGBA")
    input_mask = Image.open(mask.file).convert("RGBA")

    base_path = "C:/uploads"

    # Save the images temporarily to disk
    temp_image_path = os.path.join(base_path, "temp_input.png")
    temp_mask_path = os.path.join(base_path, "temp_mask.png")
    output_path = os.path.join(base_path, "output")

    input_image.save(temp_image_path)
    input_mask.save(temp_mask_path)

    cmd = [
        "iopaint", "run",
        "--model=lama",
        "--device=cuda",
        f"--image={temp_image_path}",
        f"--mask={temp_mask_path}",
        f"--output={output_path}"
    ]

    # Start subprocess using cmd and wait for it to finish
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print("Cleanup process completed successfully.")
        # Load the output image
        final_image_path = os.path.join(output_path, "temp_input.png")  # Adjust the output filename as needed
        final_image = Image.open(final_image_path)

        buffered = BytesIO()
        final_image.save(buffered, format="PNG")
        buffered.seek(0)

        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Clean up temporary files
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(temp_mask_path):
            os.remove(temp_mask_path)

        return JSONResponse(content={"final_image": img_str})
    else:

        # Clean up temporary files
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(temp_mask_path):
            os.remove(temp_mask_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"cleanup 중 오류가 발생했습니다. : {result.returncode}")

