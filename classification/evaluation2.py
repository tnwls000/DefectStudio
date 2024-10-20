import os
import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from datetime import datetime

# Custom Dataset 클래스 정의
class CustomDefectDataset(Dataset):
    def __init__(self, good_dir, defect_dirs, transform=None):
        self.good_dir = good_dir
        self.defect_dirs = defect_dirs
        self.transform = transform
        self.image_paths = []
        self.labels = []

        self.image_counts = {'good': 0, 'defect': 0}

        # good 이미지 로드
        if os.path.exists(good_dir):
            good_images = [os.path.join(good_dir, fname) for fname in os.listdir(good_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.image_paths.extend([(img, 0) for img in good_images])
            self.image_counts['good'] += len(good_images)

        # defect 이미지 로드
        for defect_dir in defect_dirs:
            if os.path.exists(defect_dir):
                defect_images = [os.path.join(defect_dir, fname) for fname in os.listdir(defect_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.image_paths.extend([(img, 1) for img in defect_images])
                self.image_counts['defect'] += len(defect_images)

        print(f"Good Images: {self.image_counts['good']}, Defect Images: {self.image_counts['defect']}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path, label = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label

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

# 모델 초기화 함수 (모델을 불러오는 부분 추가)
def initialize_model(model_name, num_classes, load_from=None):
    if load_from is not None and os.path.exists(load_from):
        print(f"Loading full model from {load_from}")
        model = torch.load(load_from, map_location=device)  # 전체 모델을 불러옴
    else:
        # 모델을 새로 초기화
        if model_name == 'efficientnet_v2_s':
            model = models.efficientnet_v2_s(pretrained=False)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif model_name == 'resnet34':
            model = models.resnet34(pretrained=False)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_name == 'mobilenet_v3_small':
            model = models.mobilenet_v3_small(pretrained=False)
            model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    return model

# 평가 결과 저장 함수
def save_evaluation_results(results, output_file):
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Evaluation results saved to {output_file}")

# 모델 평가 수행 함수
def evaluate_saved_models(model_names, test_loaders_dict, categories, num_classes, output_dir, model_paths):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = []

    for model_name in model_names:
        print(f"=== Evaluating {model_name} ===")
        model_path = model_paths.get(model_name)
        if not model_path:
            print(f"No saved model found for {model_name}. Skipping...")
            continue

        model = initialize_model(model_name, num_classes, load_from=model_path)
        model = model.to(device)

        # 각 카테고리에 대해 모델 평가
        for category in categories:
            print(f"Evaluating {category} with {model_name}")
            auc_score, average_precision, accuracy = evaluate_model(model, {'test': test_loaders_dict[category]})
            print(f"{category} - {model_name} - ROC-AUC: {auc_score:.4f}, AP: {average_precision:.4f}, ACC: {accuracy:.4f}\n")

            # 평가 결과 저장
            results.append({
                'Model': model_name,
                'Category': category,
                'ROC-AUC': auc_score,
                'Average Precision': average_precision,
                'Accuracy': accuracy
            })

    # 평가 결과를 CSV 파일로 저장
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"evaluation_results_{current_time}.csv")
    save_evaluation_results(results, output_file)

# 테스트 데이터 로더 설정
def prepare_test_loaders(categories, test_good_dirs, test_defect_dirs, batch_size):
    test_loaders_dict = {}
    print("Preparing test images...")
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    for category, good_dir, defect_info in zip(categories, test_good_dirs, test_defect_dirs):
        test_dataset = CustomDefectDataset(good_dir, defect_info['defects'], transform=test_transform)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        test_loaders_dict[category] = test_loader

    return test_loaders_dict

# 하이퍼파라미터 설정 및 모델 경로 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
base_dir = r'J:\conductzero\dataset\mvtec_anomaly_detection_evenly'
categories = ['bottle', 'cable', 'capsule', 'carpet', 'grid', 'hazelnut', 'leather', 'metal_nut', 'pill', 'screw', 'tile', 'toothbrush', 'transistor', 'wood', 'zipper']
test_good_dirs = [os.path.join(base_dir, category, 'test', 'good') for category in categories]
test_defect_dirs = [
    {
        'category': category,
        'defects': [os.path.join(base_dir, category, 'test', defect) for defect in os.listdir(os.path.join(base_dir, category, 'test')) if defect != 'good']
    }
    for category in categories
]

# 모델 이름 리스트 및 미리 학습된 모델 경로
model_names = ["efficientnet_v2_s", "resnet34", "mobilenet_v3_small"]

model_type = "full"
model_dir = "20241004074323"

model_paths = {
    "efficientnet_v2_s": fr"results\{model_dir}\efficientnet_v2_s_{model_type}_model.pth",
    "resnet34": fr"results\{model_dir}\resnet34_{model_type}_model.pth",
    "mobilenet_v3_small": fr"results\{model_dir}\mobilenet_v3_small_{model_type}_model.pth"
}

batch_size = 16
num_classes = 2
output_dir = "results"

# 테스트 데이터 로더 준비
test_loaders_dict = prepare_test_loaders(categories, test_good_dirs, test_defect_dirs, batch_size)

# 모델 평가 수행
evaluate_saved_models(model_names, test_loaders_dict, categories, num_classes, output_dir, model_paths)
