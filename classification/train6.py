from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from torch.optim import Adam
import numpy as np

# 학습 시 MultiCategoryGoodDataset 구현 (여러 카테고리의 good 데이터 포함)
class MultiCategoryGoodDataset(Dataset):
    def __init__(self, root_dirs, transform=None):
        self.root_dirs = root_dirs
        self.transform = transform
        self.image_paths = []

        # 모든 카테고리의 good 이미지 파일들을 로드
        for root_dir in root_dirs:
            self.image_paths.extend(
                [os.path.join(root_dir, fname) for fname in os.listdir(root_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
            )

        # 디버깅을 위한 출력
        if len(self.image_paths) == 0:
            print(f"Warning: No images found in the specified directories: {root_dirs}")
        else:
            print(f"Found {len(self.image_paths)} images in the specified directories.")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        label = 0  # 모든 라벨을 0 (good)으로 설정
        return image, label


# 테스트 시 CustomDataset 구현 (good과 defect 모두 포함)
class CustomDefectDataset(Dataset):
    def __init__(self, good_dir, defect_dirs, transform=None):
        self.good_dir = good_dir
        self.defect_dirs = defect_dirs
        self.transform = transform

        # good 이미지 경로 및 라벨 (0)
        self.image_paths = [(os.path.join(good_dir, fname), 0) for fname in os.listdir(good_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # defect 이미지 경로 및 라벨 (1)
        for defect_dir in defect_dirs:
            self.image_paths.extend([(os.path.join(defect_dir, fname), 1) for fname in os.listdir(defect_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path, label = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, label

# 데이터 경로 설정
base_dir = r'J:\conductzero\dataset\mvtec_anomaly_detection'

# 모든 카테고리의 good 데이터 경로 리스트
# categories = ['hazelnut', 'bottle', 'cable', 'capsule', 'carpet', 'grid', 'leather', 'metal_nut', 'pill', 'screw', 'tile', 'toothbrush', 'transistor', 'wood', 'zipper']
categories = ['bottle']
train_dirs = [os.path.join(base_dir, category, 'train', 'good') for category in categories]

# 테스트 경로 설정 (카테고리별로 테스트 데이터 구성)
test_good_dirs = [os.path.join(base_dir, category, 'test', 'good') for category in categories]
test_defect_dirs = [
    {
        'category': category,
        'defects': [os.path.join(base_dir, category, 'test', defect) for defect in os.listdir(os.path.join(base_dir, category, 'test')) if defect != 'good']
    }
    for category in categories
]

# 경로 확인
print(f"Train directories: {train_dirs}")
print(f"Test good directories: {test_good_dirs}")
for test_defect_dir in test_defect_dirs:
    print(f"Defect directories for {test_defect_dir['category']}: {test_defect_dir['defects']}")

# 하이퍼파라미터 설정
batch_size = 16
num_epochs = 3
learning_rate = 0.001
num_classes = 2  # good과 defect

# 학습 데이터 로더 (여러 카테고리의 good 데이터 사용)
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
train_dataset = MultiCategoryGoodDataset(train_dirs, transform=train_transform)
print(f"Total images in training dataset: {len(train_dataset)}")  # 디버깅을 위한 출력
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

# 모델 초기화 함수
def initialize_model(model_name, num_classes, pretrained=True):
    if model_name == 'efficientnet_v2_s':
        model = models.efficientnet_v2_s(pretrained=pretrained)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    else:
        raise ValueError("Invalid model name, exiting...")
    return model

# 학습 함수 정의
def train_model(model, dataloaders, criterion, optimizer, num_epochs=20, model_save_path="best_model.pth"):
    best_model_wts = model.state_dict()
    best_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)

        for phase in ['train']:
            model.train()
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects.double() / len(dataloaders[phase].dataset)

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # 가장 좋은 모델 가중치를 저장
            if phase == 'train' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = model.state_dict()
                torch.save(best_model_wts, model_save_path)  # 모델 가중치 저장
                print(f"Best model weights saved to {model_save_path} with accuracy {best_acc:.4f}")

    # 가장 좋은 가중치로 모델 로드
    model.load_state_dict(best_model_wts)
    return model

# 평가 함수 정의
def evaluate_model(model, dataloaders):
    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for inputs, labels in dataloaders['test']:
            inputs = inputs.to(device)
            labels = labels.to(device)

            # 모델 출력 및 예측 확률, 라벨 출력
            outputs = model(inputs)
            print(f"Model outputs shape: {outputs.shape}")
            print(f"Model outputs: {outputs[:5].cpu().numpy()}")  # 첫 5개 출력

            probs = torch.softmax(outputs, dim=1)  # 확률로 변환
            print(f"Predicted probabilities shape: {probs.shape}")
            print(f"Predicted probabilities: {probs[:5].cpu().numpy()}")  # 첫 5개 출력

            preds = torch.argmax(probs, dim=1)  # 예측 클래스 (0 또는 1)
            print(f"Predicted labels: {preds[:5].cpu().numpy()}")  # 첫 5개 출력

            print(f"Actual labels: {labels[:5].cpu().numpy()}")  # 첫 5개 출력

            # 라벨과 예측 확률 값을 리스트에 추가
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(probs[:, 1].cpu().numpy())  # 비정상 클래스의 확률 값 사용

    # ROC-AUC 계산 (이진 분류)
    auc_score = roc_auc_score(all_labels, all_preds)

    # AP 계산
    precision, recall, _ = precision_recall_curve(all_labels, all_preds)
    average_precision = auc(recall, precision)
    print(f"Average Precision (AP): {average_precision:.4f}")

    return auc_score, average_precision

# 각 카테고리의 테스트 데이터 로더 (good과 defect 모두 사용)
test_loaders_dict = {}
for category, good_dir, defect_info in zip(categories, test_good_dirs, test_defect_dirs):
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 해당 카테고리의 CustomDefectDataset 생성
    test_dataset = CustomDefectDataset(good_dir, defect_info['defects'], transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    test_loaders_dict[category] = test_loader

# 모델 초기화
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = 'efficientnet_v2_s'
model_save_path = "efficientnet_v2_s_best2.pth"
model = initialize_model(model_name, num_classes)
model = model.to(device)

# 학습
criterion = nn.CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr=learning_rate)
dataloaders_dict = {'train': train_loader}
model = train_model(model, dataloaders_dict, criterion, optimizer, num_epochs, model_save_path)

# 전체 모델 저장
torch.save(model, "efficientnet_v2_s_full_model2.pth")
print("Full model saved as 'efficientnet_v2_s_full_model.pth'")

# 각 카테고리에 대해 모델 평가
for category in categories:
    print(f"=== Evaluating {category} ===")
    auc_score, average_precision = evaluate_model(model, {'test': test_loaders_dict[category]})
    print(f"{category} - ROC-AUC: {auc_score:.4f}, AP: {average_precision:.4f}\n")
