import os
import torch
import lpips
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import torchvision.transforms.functional as TF
from torchvision import transforms

# LPIPS 계산을 위한 클래스 설정 (AlexNet 사용)
lpips_alex = lpips.LPIPS(net='alex').cuda()  # LPIPS는 CUDA 장치에 놓도록 설정

# Custom Dataset 클래스 정의 (평가용)
class CustomDataset(Dataset):
    def __init__(self, dir1, dir2, transform=None):
        self.dir1 = dir1
        self.dir2 = dir2
        self.transform = transform
        self.image_pairs = [(os.path.join(dir1, f), os.path.join(dir2, f)) for f in os.listdir(dir1) if f in os.listdir(dir2)]

        if len(self.image_pairs) == 0:
            print(f"Warning: No matching image pairs found between {dir1} and {dir2}")

    def __len__(self):
        return len(self.image_pairs)

    def __getitem__(self, idx):
        img1_path, img2_path = self.image_pairs[idx]
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')

        # 이미지를 uint8 형식의 텐서로 변환
        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        img1 = TF.to_tensor(img1).mul(255).byte()  # float -> uint8 변환
        img2 = TF.to_tensor(img2).mul(255).byte()

        return img1, img2

# 이미지 전처리 설정 (LPIPS 계산을 위한 이미지 크기 조정)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
])

# 데이터 로더 설정
def prepare_dataloader_lpips(dir1, dir2, batch_size):
    dataset = CustomDataset(dir1, dir2, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    return dataloader

# LPIPS 계산 함수
def calculate_lpips(dir1, dir2, batch_size):
    print(f"=== Calculating LPIPS ===")

    # 데이터 로더 설정
    dataloader = prepare_dataloader_lpips(dir1, dir2, batch_size)

    # 데이터 로더가 비어 있을 경우 처리
    if len(dataloader) == 0:
        print("Error: No valid image pairs found for comparison.")
        return 0  # LPIPS를 0으로 반환하여 오류 방지

    # LPIPS 계산
    lpips_total = 0.0
    with torch.no_grad():
        for img1, img2 in dataloader:
            img1, img2 = img1.cuda(), img2.cuda()  # 두 텐서를 모두 CUDA로 옮김

            # LPIPS 계산
            lpips_value = lpips_alex(img1, img2)
            lpips_total += lpips_value.mean().item()

        # 평균 LPIPS
        avg_lpips = lpips_total / len(dataloader)

    print(f"LPIPS: {avg_lpips:.4f}")
    return avg_lpips

# 실제 예시 경로 (이미지가 있는 디렉토리)
dir1 = r'J:\conductzero\dataset\mvtec_anomaly_detection\bottle\test\broken_large'
dir2 = r'J:\conductzero\dataset\mvtec_anomaly_detection_evaluate\bottle\train\defect\broken_large'

# 배치 크기 설정
batch_size = 16

# LPIPS 계산
lpips_score = calculate_lpips(dir1, dir2, batch_size)

# 결과 출력
print(f"LPIPS: {lpips_score:.4f}")
