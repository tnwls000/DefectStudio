import os
import torch
from torch.utils.data import DataLoader, Dataset
from torchmetrics.image.kid import KernelInceptionDistance
from PIL import Image
import torchvision.transforms.functional as TF
from torchvision import transforms

# 적은 수에 맞춰서 비교

# KID 계산 클래스 초기화 (Inception 네트워크 사용)
kid = KernelInceptionDistance(subset_size=8).cuda()  # KID는 CUDA 장치에서 실행

# Custom Dataset 클래스 정의 (평가용)
class CustomDataset(Dataset):
    def __init__(self, dir1, dir2, transform=None):
        # 두 디렉토리의 이미지 목록을 정렬하여 순차적으로 쌍을 만듦
        self.dir1_images = sorted([os.path.join(dir1, f) for f in os.listdir(dir1) if f.endswith(('png', 'jpg', 'jpeg'))])
        self.dir2_images = sorted([os.path.join(dir2, f) for f in os.listdir(dir2) if f.endswith(('png', 'jpg', 'jpeg'))])
        self.transform = transform

        # 디렉토리 간의 이미지 개수가 다르면 경고 메시지 출력
        if len(self.dir1_images) != len(self.dir2_images):
            print(f"Warning: Unequal number of images in {dir1} and {dir2}. Using the smaller number of images.")

    def __len__(self):
        # 작은 쪽에 맞춰서 데이터셋 길이를 설정
        return min(len(self.dir1_images), len(self.dir2_images))

    def __getitem__(self, idx):
        img1_path = self.dir1_images[idx]
        img2_path = self.dir2_images[idx]
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')

        # 이미지를 uint8 형식의 텐서로 변환
        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        img1 = TF.to_tensor(img1).mul(255).byte()  # float -> uint8 변환
        img2 = TF.to_tensor(img2).mul(255).byte()

        return img1, img2

# 이미지 전처리 설정 (KID 계산을 위한 이미지 크기 조정)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
])

# 데이터 로더 설정
def prepare_dataloader_kid(dir1, dir2, batch_size):
    dataset = CustomDataset(dir1, dir2, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    return dataloader

# KID 계산 함수
def calculate_kid(dir1, dir2, batch_size):
    print(f"=== Calculating KID ===")

    # 데이터 로더 설정
    dataloader = prepare_dataloader_kid(dir1, dir2, batch_size)

    # 데이터 로더가 비어 있을 경우 처리
    if len(dataloader) == 0:
        print("Error: No valid image pairs found for comparison.")
        return 0  # KID를 0으로 반환하여 오류 방지

    # KID 계산
    with torch.no_grad():
        for img1, img2 in dataloader:
            img1, img2 = img1.cuda(), img2.cuda()  # 두 텐서를 모두 CUDA로 옮김

            # KID 계산을 위한 피쳐 추출
            kid.update(img1, real=True)
            kid.update(img2, real=False)

        # KID 스코어 계산 (한 번만 계산)
        kid_mean, kid_std = kid.compute()

        # KID 상태 초기화
        kid.reset()

    # 결과는 한 번만 출력
    print(f"KID Mean: {kid_mean.item():.4f}, KID Std: {kid_std.item():.4f}")
    return kid_mean.item(), kid_std.item()


# 실제 예시 경로 (이미지가 있는 디렉토리)
# real
dir1 = r'J:\conductzero\dataset\mvtec_anomaly_detection_evenly_gen\metal_nut\test\bent'
# gen
dir2 = r'J:\conductzero\project\be\S11P21S001\ai\classification\gen_data\output_images_choose\metal_nut\bent'

# 배치 크기 설정
batch_size = 16

# KID 계산
kid_mean, kid_std = calculate_kid(dir1, dir2, batch_size)

# 결과 출력
print(f"KID Mean: {kid_mean:.4f}, KID Std: {kid_std:.4f}")
