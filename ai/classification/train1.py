import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import transforms, models
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from datetime import datetime
from PIL import Image
from torch.utils.data import Dataset
import glob

# 데이터셋 클래스 정의
class MVTecDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.classes = []  # 클래스 목록 초기화
        self._load_images()

    def _load_images(self):
        classes = os.listdir(self.root_dir)
        for class_idx, cls in enumerate(classes):
            class_path = os.path.join(self.root_dir, cls, 'train', 'good')
            if os.path.exists(class_path):
                for img_path in glob.glob(os.path.join(class_path, "*.png")):
                    self.image_paths.append(img_path)
                    # self.labels.append(class_idx) # 다중 클래스 학습
                    self.labels.append(0)
            # 클래스 이름을 classes 리스트에 추가
            # self.classes.append(cls) # 다중 클래스 지정
            self.classes.append('good')

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


# 데이터 전처리
pretrained_size = 224
pretrained_means = [0.485, 0.456, 0.406]
pretrained_stds = [0.229, 0.224, 0.225]
transform = transforms.Compose([
    transforms.Resize(pretrained_size),
    transforms.RandomRotation(5),
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomCrop(pretrained_size, padding=10),
    # transforms.AutoAugment(policy=transforms.AutoAugmentPolicy.IMAGENET),  # AutoAugment 적용
    transforms.ToTensor(),
    transforms.Normalize(pretrained_means, pretrained_stds),
    transforms.RandomErasing(p=0.1),  # 랜덤 지우기 적용
])

# 데이터셋 경로
dataset_path = 'J:/conductzero/dataset/mvtec_anomaly_detection'
train_dataset = MVTecDataset(root_dir=dataset_path, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_classes = 1  # 이진 분류를 위해 num_classes를 1로 설정

# 손실 함수 및 학습 함수 정의
criterion = nn.BCEWithLogitsLoss()  # 이진 분류를 위해 BCEWithLogitsLoss 사용

# Accuracy 계산 함수
def calculate_accuracy(outputs, labels):
    preds = torch.round(torch.sigmoid(outputs))
    corrects = torch.sum(preds == labels)
    return corrects.item() / len(labels)

# 학습 함수 수정 (스케줄러 추가)
def train_model(model_name, model, optimizer, scheduler=None, num_epochs=10):
    model.to(device)
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        running_corrects = 0
        for inputs, labels in train_loader:
            # print("Inputs:", inputs)
            # print("Labels:", labels)
            inputs, labels = inputs.to(device), labels.float().unsqueeze(1).to(device)  # 레이블을 float으로 변환하고 형태 변경
            optimizer.zero_grad()
            outputs = model(inputs)

            # 손실 함수 계산
            loss = criterion(outputs, labels)


            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            running_corrects += calculate_accuracy(outputs, labels) * len(labels)

        # 에폭이 끝난 후 스케줄러 업데이트
        if scheduler:
            scheduler.step()

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = running_corrects / len(train_dataset)
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}')
        print(f'running_loss: {running_loss}, train_loader: { len(train_loader)}')
        print(f'running_corrects: {running_corrects}, train_loader: { len(train_dataset)}')


    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    torch.save(model.state_dict(), f'{model_name}_fine_tuned_{current_time}.pth')


# ResNet-34 모델 학습
def fine_tune_resnet34():
    model_name = "resnet34"
    model = models.resnet34(weights=models.ResNet34_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)
    train_model(model_name, model, optimizer, scheduler)


# EfficientNet v2 s 모델 학습
def fine_tune_efficientnet_v2_s():
    model_name = "efficientnet_v2_s"
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    # model.classifier[1] = nn.Linear(model.classifier[1].in_features, 1)  # 이진 분류를 위한 출력층 조정

    # 가중치 초기화 추가
    # nn.init.xavier_uniform_(model.classifier[1].weight)
    # nn.init.zeros_(model.classifier[1].bias)

    # 옵티마이저 설정
    # optimizer = optim.SGD(model.parameters(), lr=0.5, momentum=0.9, weight_decay=2e-5)
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)  # 학습률을 낮게 설정

    # 스케줄러 설정
    # scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=600, eta_min=1e-5)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5, eta_min=1e-6)

    # 학습
    train_model(model_name, model, optimizer, scheduler)


# ConvNeXt Tiny 모델 학습
def fine_tune_convnext_tiny():
    model_name = "convnext_tiny"
    model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1)
    model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.05)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=600, eta_min=1e-6)
    train_model(model_name, model, optimizer, scheduler)


# MobileNet v3 Small 모델 학습
def fine_tune_mobilenet_v3_small():
    model_name = "mobilenet_v3_small"
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    optimizer = optim.RMSprop(model.parameters(), lr=0.064, alpha=0.9, momentum=0.9, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.973)
    train_model(model_name, model, optimizer, scheduler)


def main():
    # fine_tune_resnet34()
    fine_tune_efficientnet_v2_s()
    # fine_tune_convnext_tiny()
    # fine_tune_mobilenet_v3_small()


if __name__ == '__main__':
    main()
