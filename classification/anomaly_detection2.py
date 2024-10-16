import os
import numpy as np
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms, models
from PIL import Image
from tqdm import tqdm
from datetime import datetime

# 공통 데이터 전처리 설정
pretrained_size = 224
pretrained_means = [0.485, 0.456, 0.406]
pretrained_stds = [0.229, 0.224, 0.225]
transform = transforms.Compose([
    transforms.Resize(pretrained_size),
    transforms.ToTensor(),
    transforms.Normalize(pretrained_means, pretrained_stds)
])

# 테스트 데이터 경로 설정
test_root = os.path.join('J:', 'conductzero', 'dataset', 'mvtec_anomaly_detection')

# 특정 시간 폴더명 (사용자가 수정할 변수)
specified_time_folder = "20240927005345"  # 예: "20230925" -> 매번 이 변수를 수정

# 모델 경로 설정
model_dir = os.path.join('results', specified_time_folder)

current_time = datetime.now().strftime('%Y%m%d%H%M%S')
# 출력 경로 설정 (현재 시각으로 하위 폴더 추가)
output_root = os.path.join('results', specified_time_folder, 'anomaly_maps', current_time)
# 출력 경로 디렉토리 생성
os.makedirs(output_root, exist_ok=True)

# 모델별 예측 함수 정의
def process_images(model, device, output_root):
    # 모든 카테고리와 결함 타입에 대해 처리
    for category in os.listdir(test_root):
        category_path = os.path.join(test_root, category, 'test')
        if not os.path.isdir(category_path):
            continue  # 경로가 디렉토리가 아니면 건너뜀

        # 하위 결함 폴더 탐색
        for defect_type in os.listdir(category_path):
            defect_path = os.path.join(category_path, defect_type)
            if not os.path.isdir(defect_path):
                continue  # 결함 폴더가 아니면 건너뜀

            # 출력 디렉토리 설정 (test 추가)
            output_dir = os.path.join(output_root, category, 'test', defect_type)
            os.makedirs(output_dir, exist_ok=True)

            print(f"\nProcessing category: {category}, defect type: {defect_type}")

            # 각 결함 폴더의 모든 이미지에 대해 처리
            for img_name in tqdm(os.listdir(defect_path)):
                img_path = os.path.join(defect_path, img_name)
                if os.path.isfile(img_path):
                    try:
                        img = Image.open(img_path).convert('RGB')
                        img_tensor = transform(img).unsqueeze(0).to(device)

                        with torch.no_grad():
                            output = model(img_tensor)
                            probs = torch.softmax(output, dim=1)
                            anomaly_score = probs[:, 1].item()  # 비정상 클래스의 확률

                        # 이상 지도 생성
                        anomaly_map = np.full((img.height, img.width), anomaly_score * 255, dtype=np.uint8)
                        anomaly_map_path = os.path.join(output_dir, img_name.replace('.png', '.tiff'))

                        # TIFF 형식으로 이상 지도 저장
                        Image.fromarray(anomaly_map).save(anomaly_map_path)
                    except Exception as e:
                        print(f"Error processing {img_path}: {e}")

# 모델 로드 및 설정 함수
def load_model(model_name):
    if model_name == "resnet34":
        model = models.resnet34(weights=models.ResNet34_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, 2)  # 이진 분류
    elif model_name == "efficientnet_v2_s":
        model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)  # 이진 분류
    elif model_name == "convnext_tiny":
        model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1)
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, 2)  # 이진 분류
    elif model_name == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, 2)  # 이진 분류
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

    return model

def main():
    # 모델 이름 리스트
    model_names = ["efficientnet_v2_s", "resnet34", "convnext_tiny", "mobilenet_v3_small"]

    for model_name in model_names:
        print(f"Processing with model: {model_name}")

        # 모델 경로 설정
        model_path = os.path.join(model_dir, f'{model_name}_best_model.pth')

        # 모델 로드
        model = load_model(model_name)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')), strict=False)
        model.eval()

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)

        # 모델별 출력 디렉토리 설정
        model_output_root = os.path.join(output_root, model_name)
        os.makedirs(model_output_root, exist_ok=True)

        # 선택된 모델로 이미지 처리
        process_images(model, device, model_output_root)

if __name__ == '__main__':
    main()
