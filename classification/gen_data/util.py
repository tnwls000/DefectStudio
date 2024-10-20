import json
from PIL import Image
import random
from datetime import datetime
import re
import os

# Pipe 설정 정보를 JSON 형식으로 저장하는 함수
def save_pipe_info(output_dir, prompt, num_samples, num_inference_steps, guidance_scale, seed, saved_files):
    json_file = os.path.join(output_dir, "pipe_info.json")

    # JSON 파일이 이미 존재하면 그 내용을 읽고 새로운 데이터를 이어서 추가
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                pipe_info_list = json.load(f)
            except json.JSONDecodeError:
                # JSON 파일이 손상된 경우 빈 리스트로 시작
                pipe_info_list = []
    else:
        # JSON 파일이 없으면 새로운 리스트 생성
        pipe_info_list = []

    # 타임스탬프 생성
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 새로운 pipe 정보 추가
    new_pipe_info = {
        "timestamp": timestamp,  # 타임스탬프 추가
        "prompt": prompt,
        "num_samples": num_samples,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "seed": seed,
        "saved_files": saved_files
    }

    # 기존 정보 리스트에 새 항목 추가
    pipe_info_list.append(new_pipe_info)

    # JSON 파일에 저장 (원래 내용을 유지하면서 이어서 쓰기)
    with open(json_file, 'w') as f:
        json.dump(pipe_info_list, f, indent=4)

    print(f"Pipe information saved to: {json_file}")



# 이미지 그리드를 생성하는 함수 정의
def image_grid(imgs, rows, cols, resize=256):
    if resize is not None:
        imgs = [img.resize((resize, resize)) for img in imgs]
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))

    return grid

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