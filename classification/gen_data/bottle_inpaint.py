from diffusers import AutoPipelineForInpainting
import torch
import numpy as np
import os
from PIL import Image
import random
from datetime import datetime
from util import save_pipe_info

# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"]="1"

# 이미지 그리드를 생성하는 함수 정의
def image_grid(imgs, rows, cols, resize=256):
    if resize is not None:
        imgs = [img.resize((resize, resize)) for img in imgs]
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))

    return grid

import re

# 가장 최근 저장된 파일의 숫자를 파악하는 함수
def get_latest_file_number(output_dir):
    existing_files = [f for f in os.listdir(output_dir) if f.startswith('g') and f.endswith('.png')]
    if not existing_files:
        return -1  # 저장된 파일이 없으면 -1 반환
    existing_numbers = [int(re.findall(r'\d+', f)[0]) for f in existing_files]
    return max(existing_numbers)

# 저장할 파일명 결정하는 함수
def get_new_filename(output_dir, latest_number):
    new_number = latest_number + 1
    return f"g{new_number:03d}.png"

# Stable Diffusion 모델 초기화 및 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
output_dir = "output_images/bottle/broken_small"
os.makedirs(output_dir, exist_ok=True)

# /home/j-j11s001/project
# Inpaint 파이프라인 초기화
inpaint_pipe = AutoPipelineForInpainting.from_pretrained(
    "model/model_bottle", torch_dtype=torch.float16
).to(device)

# inpaint_pipe = AutoPipelineForInpainting.from_pretrained(
#     "/home/j-j11s001/project/bumsoo/dataset/dreambooth_output/bottle_contamination_test_20240930120723_dreambooth", torch_dtype=torch.float16
# ).to(device)

# inpaint_pipe = AutoPipelineForInpainting.from_pretrained(
#     "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16
# ).to(device)


# # Inpaint 파이프라인 초기화
# inpaint_pipe = AutoPipelineForInpainting.from_pretrained(
#     "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16
# ).to(device)

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

generator = torch.Generator(device="cuda").manual_seed(random.randint(0, 2 ** 32 - 1))

# Inpainting 처리
init_image = Image.open("input_images/bottle/image.png").resize((512, 512)).convert("RGB")
mask_image = Image.open("input_images/bottle/mask2.jpg").resize((512, 512)).convert("L")

# PIL 이미지를 numpy 배열로 변환한 후 텐서로 변환
init_image_np = np.array(init_image)  # numpy 배열로 변환
mask_image_np = np.array(mask_image).astype(np.float32) / 255.0  # 마스크를 [0, 255]에서 [0, 1]로 변환

# 텐서로 변환 (이미지의 dtype을 float로 맞춤)
init_image_tensor = torch.tensor(init_image_np).permute(2, 0, 1).unsqueeze(0).float()  # (C, H, W) -> (1, C, H, W)
mask_image_tensor = torch.tensor(mask_image_np).unsqueeze(0).unsqueeze(0).float()  # (H, W) -> (1, 1, H, W)

# 텐서 크기 확인
print(f"이미지 텐서 크기: {init_image_tensor.size()}")
print(f"마스크 텐서 크기: {mask_image_tensor.size()}")

print(f"Init image size: {init_image.size}")
print(f"Mask image size: {mask_image.size}")

# 프롬프트 설정
# prompt = "a photo of a broken large bottle, high quality, showing realistic cracks"
# prompt = "a photo of a broken small bottle, high quality, showing realistic cracks"

# prompt = "a photo of a contamination bottle, high quality"
# prompt = "a photo of a broken large bottle, high quality"
prompt = "a photo of a broken small bottle, high quality"
num_samples = 10
num_inference_steps = 100  # 단계 수를 증가
guidance_scale = 10.0  # 가이던스 스케일을 높여 모델의 수정 범위를 넓힘

# Inpainting 과정 실행
try:

    # Pipe 정보를 JSON 형식으로 저장
    save_pipe_info(output_dir, prompt, num_samples, num_inference_steps, guidance_scale)

    result = inpaint_pipe(
        prompt=prompt,
        # negative_prompt=negative_prompt,
        image=init_image,
        mask_image=mask_image,
        num_inference_steps=num_inference_steps,  # 단계 수를 증가
        guidance_scale=guidance_scale,  # 가이던스 스케일을 높여 모델의 수정 범위를 넓힘
        generator=generator,
        num_images_per_prompt=num_samples
    )

    # 가장 최근 파일의 번호 파악
    latest_number = get_latest_file_number(output_dir)

    # 개별 생성된 이미지 저장
    for idx, generated_image in enumerate(result.images):
        output_file = os.path.join(output_dir, get_new_filename(output_dir, latest_number + idx))
        generated_image.save(output_file)
        print(f"Image saved to: {output_file}")


    # result.images.insert(0, init_image)  # 첫번째 이미지를 원본 이미지로 추가
    # grid_image = image_grid(result.images, 1, num_samples + 1)
    #
    # # 그리드 이미지 저장
    # grid_output_file = os.path.join(output_dir, f"grid_image_{timestamp}.png")
    # grid_image.save(grid_output_file)
    # print(f"Image grid saved to: {grid_output_file}")
    #
    # # 개별 생성된 이미지 저장 (첫 번째 이미지)
    # generated_image = result.images[0]
    # output_file = os.path.join(output_dir, f"generated_image_{timestamp}.png")
    # output_mask_file = os.path.join(output_dir, f"generate_mask_image_{timestamp}.png")
    # generated_image.save(output_file)
    # mask_image.save(output_mask_file)
    # print(f"Image saved to: {output_file}, {output_mask_file}")
except Exception as e:
    print(f"Error during inpainting generation: {e}")