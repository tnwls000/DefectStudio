import os
import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

# 현재 시간 기반으로 폴더 생성
current_time = datetime.now().strftime('%Y%m%d%H%M%S')
output_dir = os.path.join("results", current_time)
os.makedirs(output_dir, exist_ok=True)  # 결과를 저장할 폴더 생성

# 데이터셋 클래스 정의
class MultiCategoryGoodAndDefectDataset(Dataset):
    def __init__(self, root_dirs, transform=None):
        self.root_dirs = root_dirs
        self.transform = transform
        self.image_paths = []
        self.labels = []

        for root_dir in root_dirs:
            good_dir = os.path.join(root_dir, 'good')
            if os.path.exists(good_dir):
                good_images = [os.path.join(good_dir, fname) for fname in os.listdir(good_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.image_paths.extend(good_images)
                self.labels.extend([0] * len(good_images))

            defect_dir = os.path.join(root_dir, 'defect')
            if os.path.exists(defect_dir):
                for defect_subdir in os.listdir(defect_dir):
                    defect_subdir_path = os.path.join(defect_dir, defect_subdir)
                    if os.path.isdir(defect_subdir_path):
                        defect_images = [os.path.join(defect_subdir_path, fname) for fname in os.listdir(defect_subdir_path) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        self.image_paths.extend(defect_images)
                        self.labels.extend([1] * len(defect_images))

        if len(self.image_paths) == 0:
            print(f"Warning: No images found in the specified directories: {root_dirs}")
        else:
            print(f"Found {len(self.image_paths)} images in the specified directories.")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label

class CustomDefectDataset(Dataset):
    def __init__(self, good_dir, defect_dirs, transform=None):
        self.good_dir = good_dir
        self.defect_dirs = defect_dirs
        self.transform = transform
        self.image_paths = [(os.path.join(good_dir, fname), 0) for fname in os.listdir(good_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]

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
categories = ['hazelnut', 'bottle', 'cable', 'capsule', 'carpet', 'grid', 'leather', 'metal_nut', 'pill', 'screw', 'tile', 'toothbrush', 'transistor', 'wood', 'zipper']
train_dirs = [os.path.join(base_dir, category, 'train') for category in categories]
test_good_dirs = [os.path.join(base_dir, category, 'test', 'good') for category in categories]
test_defect_dirs = [
    {
        'category': category,
        'defects': [os.path.join(base_dir, category, 'test', defect) for defect in os.listdir(os.path.join(base_dir, category, 'test')) if defect != 'good']
    }
    for category in categories
]

# 하이퍼파라미터 설정
batch_size = 16
num_epochs = 20
learning_rate = 0.0005
num_classes = 2

# 학습 데이터 로더 설정
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
train_dataset = MultiCategoryGoodAndDefectDataset(train_dirs, transform=train_transform)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# 평가 함수 정의
def evaluate_model(model, dataloaders):
    model.eval()
    all_labels = []
    all_preds = []
    running_corrects = 0
    total_samples = 0

    with torch.no_grad():
        for inputs, labels in dataloaders['test']:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(probs[:, 1].cpu().numpy())

            running_corrects += torch.sum(preds == labels.data)
            total_samples += labels.size(0)

    accuracy = running_corrects.double() / total_samples
    auc_score = roc_auc_score(all_labels, all_preds)
    precision, recall, _ = precision_recall_curve(all_labels, all_preds)
    average_precision = auc(recall, precision)
    return auc_score, average_precision, accuracy.item()

# 모델 초기화 함수
def initialize_model(model_name, num_classes, pretrained=True):
    if model_name == 'efficientnet_v2_s':
        model = models.efficientnet_v2_s(pretrained=pretrained)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif model_name == 'resnet34':
        model = models.resnet34(pretrained=pretrained)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif model_name == 'convnext_tiny':
        model = models.convnext_tiny(pretrained=pretrained)
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    elif model_name == 'mobilenet_v3_small':
        model = models.mobilenet_v3_small(pretrained=pretrained)
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    else:
        raise ValueError(f"Invalid model name: {model_name}")
    return model

# 학습 함수 정의
def train_model(model, dataloaders, criterion, optimizer, num_epochs=20, model_save_path="best_model.pth", save_dir=None, model_name="model"):
    best_model_wts = model.state_dict()
    best_acc = 0.0

    # 학습 기록을 저장할 리스트 초기화
    train_losses = []
    train_accuracies = []

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

            # 현재 에폭의 로스와 정확도를 저장
            train_losses.append(epoch_loss)
            train_accuracies.append(epoch_acc.item())

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # 가장 좋은 모델 가중치를 저장
            if phase == 'train' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = model.state_dict()
                torch.save(best_model_wts, model_save_path)  # 모델 가중치 저장
                print(f"Best model weights saved to {model_save_path} with accuracy {best_acc:.4f}")

    # 가장 좋은 가중치로 모델 로드
    model.load_state_dict(best_model_wts)

    # 학습 기록을 그래프로 시각화하고 저장
    if save_dir is not None:
        plot_training_history(train_losses, train_accuracies, num_epochs, save_dir, model_name)

    return model

# 학습 기록 시각화 함수 정의 및 저장
def plot_training_history(losses, accuracies, num_epochs, save_dir, model_name):
    epochs = range(1, num_epochs + 1)

    # 로스 그래프
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs, losses, 'b-', label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(f'Training Loss over Epochs - {model_name}')
    plt.legend()

    # 정확도 그래프
    plt.subplot(1, 2, 2)
    plt.plot(epochs, accuracies, 'r-', label='Training Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title(f'Training Accuracy over Epochs - {model_name}')
    plt.legend()

    plt.tight_layout()

    # 그래프를 이미지로 저장
    graph_path = os.path.join(save_dir, f'{model_name}_training_history.png')
    plt.savefig(graph_path)
    print(f"Training history graph for {model_name} saved as {graph_path}")
    plt.close()  # 그래프를 화면에 표시하지 않고 저장 후 닫음

# 평가 결과 저장 함수
def save_evaluation_results(results, output_file):
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Evaluation results saved to {output_file}")

# 모델 학습 및 평가 수행
def train_and_evaluate_models(model_names, train_loader, test_loaders_dict, categories, num_classes, learning_rate, num_epochs, output_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = []

    for model_name in model_names:
        print(f"=== Training and Evaluating {model_name} ===")

        model = initialize_model(model_name, num_classes)
        model = model.to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = Adam(model.parameters(), lr=learning_rate)
        dataloaders_dict = {'train': train_loader}

        # 모델 저장 경로
        model_save_path = os.path.join(output_dir, f"{model_name}_best_model.pth")

        # 모델 학습
        model = train_model(model, dataloaders_dict, criterion, optimizer, num_epochs, model_save_path, save_dir=output_dir, model_name=model_name)

        # 전체 모델 저장
        full_model_path = os.path.join(output_dir, f"{model_name}_full_model.pth")
        torch.save(model, full_model_path)
        print(f"Full model saved as '{full_model_path}'")

        # 각 카테고리에 대해 모델 평가
        for category in categories:
            print(f"=== Evaluating {category} with {model_name} ===")
            auc_score, average_precision, accuracy = evaluate_model(model, {'test': test_loaders_dict[category]})
            print(f"{category} - {model_name} - ROC-AUC: {auc_score:.4f}, AP: {average_precision:.4f}, ACC: {accuracy:.4f}\n")

            # 평가 결과 저장을 위해 딕셔너리에 추가
            results.append({
                'Model': model_name,
                'Category': category,
                'ROC-AUC': auc_score,
                'Average Precision': average_precision,
                'Accuracy': accuracy
            })

    # 평가 결과를 CSV 파일로 저장
    output_file = os.path.join(output_dir, f"evaluation_results_{current_time}.csv")
    save_evaluation_results(results, output_file)

# 테스트 데이터 로더 설정
test_loaders_dict = {}
for category, good_dir, defect_info in zip(categories, test_good_dirs, test_defect_dirs):
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 각 카테고리의 CustomDefectDataset 생성
    test_dataset = CustomDefectDataset(good_dir, defect_info['defects'], transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    test_loaders_dict[category] = test_loader

# 모델 이름 리스트
model_names = ["efficientnet_v2_s", "resnet34", "convnext_tiny", "mobilenet_v3_small"]

# 모델 학습 및 평가
train_and_evaluate_models(model_names, train_loader, test_loaders_dict, categories, num_classes, learning_rate, num_epochs, output_dir)

