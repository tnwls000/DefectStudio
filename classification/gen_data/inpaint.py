from diffusers import AutoPipelineForInpainting
import torch
import numpy as np
import os
from PIL import Image
import random
from datetime import datetime
from util import save_pipe_info, image_grid, get_latest_file_number, get_new_filename

# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"]="1"

category = "metal_nut"
# bent_lead, cut_lead, damaged_case, misplaced
defect = "scratch"

# Stable Diffusion 모델 초기화 및 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
output_dir = f"output_images/{category}/{defect}"
os.makedirs(output_dir, exist_ok=True)

# Inpaint 파이프라인 초기화
inpaint_pipe = AutoPipelineForInpainting.from_pretrained(
    f"model/model_{category}", torch_dtype=torch.float16
).to(device)

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

seed = random.randint(0, 2 ** 32 - 1)
generator = torch.Generator(device="cuda").manual_seed(seed)
image = "image2.png"
mask = "mask.png"

# Inpainting 처리
init_image = Image.open(f"input_images/{category}/{image}").resize((512, 512)).convert("RGB")
mask_image = Image.open(f"input_images/{category}/{mask}").resize((512, 512)).convert("L")

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
prompt = "a photo of a scratch metal nut"

num_samples = 10
num_inference_steps = 100  # 단계 수를 증가
guidance_scale = 2 # 가이던스 스케일을 높여 모델의 수정 범위를 넓힘

# Inpainting 과정 실행
try:
    saved_files = []

    print(prompt)
    print(image)
    print(mask)
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

    saved_files.append(image)
    saved_files.append(mask)

    # 가장 최근 파일의 번호 파악
    latest_number = get_latest_file_number(output_dir)

    # 개별 생성된 이미지 저장
    for idx, generated_image in enumerate(result.images):
        output_file = os.path.join(output_dir, get_new_filename(output_dir, latest_number + idx))
        generated_image.save(output_file)
        saved_files.append(output_file)  # 이미지 파일명 저장
        print(f"Image saved to: {output_file}")

    # Pipe 정보를 JSON 형식으로 저장
    save_pipe_info(output_dir, prompt, num_samples, num_inference_steps, guidance_scale, seed, saved_files)


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