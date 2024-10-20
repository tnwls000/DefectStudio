import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torch.optim import Adam
import numpy as np

# 데이터 경로 설정
base_dir = 'J:/conductzero/dataset/mvtec_anomaly_detection'
category = 'hazelnut'  # 사용할 카테고리 지정
train_dir = os.path.join(base_dir, category, 'train')  # train에는 good 데이터만 사용
test_dir = os.path.join(base_dir, category, 'test')  # test에는 good과 defect 모두 포함

# 경로 확인
print(f"Checking train directory: {train_dir}")
if not os.path.exists(train_dir):
    print(f"Error: Directory {train_dir} does not exist.")

print(f"Checking test directory: {test_dir}")
if not os.path.exists(test_dir):
    print(f"Error: Directory {test_dir} does not exist.")

# 하이퍼파라미터 설정
batch_size = 16
num_epochs = 3
learning_rate = 0.001

# 데이터 변환 설정
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
}

# 데이터 로더 설정 (train에는 good 데이터만 포함)
train_dataset = ImageFolder(train_dir, transform=data_transforms['train'])
print(train_dataset.class_to_idx)
test_dataset = ImageFolder(test_dir, transform=data_transforms['test'])
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# 클래스 수 확인 (이진 분류)
num_classes = 2  # good과 not-good (defect)
print(f'Number of classes: {num_classes}')  # 클래스 수 확인

# 모델 초기화 함수
def initialize_model(model_name, num_classes, pretrained=True):
    if model_name == 'efficientnet_v2_s':
        model = models.efficientnet_v2_s(pretrained=pretrained)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    else:
        raise ValueError("Invalid model name, exiting...")
    return model

# 학습 함수 정의
def train_model(model, dataloaders, criterion, optimizer, num_epochs=20):
    best_model_wts = model.state_dict()
    best_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)

        for phase in ['train']:
            print(phase)
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

    # all_preds가 1차원 배열이므로 2차원으로 변환하지 않고 그대로 사용
    all_preds = np.array(all_preds)  # 비정상 클래스의 확률 값

    # ROC-AUC 계산 (이진 분류)
    auc_score = roc_auc_score(all_labels, all_preds)  # multi_class 매개변수 제거

    # AP 계산
    precision, recall, _ = precision_recall_curve(all_labels, all_preds)
    average_precision = auc(recall, precision)
    print(f"Average Precision (AP): {average_precision:.4f}")

    return auc_score, average_precision

# 메인 함수 실행
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = 'efficientnet_v2_s'  # 사용할 모델 이름
model = initialize_model(model_name, num_classes)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr=learning_rate)

dataloaders_dict = {'train': train_loader, 'test': test_loader}

# 모델 학습
model = train_model(model, dataloaders_dict, criterion, optimizer, num_epochs)

# 모델 평가
evaluate_model(model, dataloaders_dict)
