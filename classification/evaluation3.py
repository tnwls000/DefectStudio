import os
import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from sklearn.metrics import confusion_matrix
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

# 평가 함수 정의
def evaluate_model_by_category(model, dataloader_good, dataloader_defect):
    model.eval()

    def evaluate_single_category(dataloader, true_label):
        all_labels = []
        all_preds = []

        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                probs = torch.softmax(outputs, dim=1)
                preds = torch.argmax(probs, dim=1)

                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())

        # 혼동 행렬 계산
        tn, fp, fn, tp = confusion_matrix(all_labels, all_preds, labels=[0, 1]).ravel()
        return tn, fp, fn, tp

    # Good 데이터셋 평가
    tn_good, fp_good, fn_good, tp_good = evaluate_single_category(dataloader_good, true_label=0)
    accuracy_good = (tp_good + tn_good) / (tp_good + fp_good + fn_good + tn_good)
    precision_good = tp_good / (tp_good + fp_good) if (tp_good + fp_good) > 0 else 0
    recall_good = tp_good / (tp_good + fn_good) if (tp_good + fn_good) > 0 else 0
    specificity_good = tn_good / (tn_good + fp_good) if (tn_good + fp_good) > 0 else 0

    # Defect 데이터셋 평가
    tn_defect, fp_defect, fn_defect, tp_defect = evaluate_single_category(dataloader_defect, true_label=1)
    accuracy_defect = (tp_defect + tn_defect) / (tp_defect + fp_defect + fn_defect + tn_defect)
    precision_defect = tp_defect / (tp_defect + fp_defect) if (tp_defect + fp_defect) > 0 else 0
    recall_defect = tp_defect / (tp_defect + fn_defect) if (tp_defect + fn_defect) > 0 else 0
    specificity_defect = tn_defect / (tn_defect + fp_defect) if (tn_defect + fp_defect) > 0 else 0

    return {
        'good': {
            'Accuracy': accuracy_good,
            'Precision': precision_good,
            'Recall': recall_good,
            'Specificity': specificity_good,
            'Confusion Matrix': {'TP': tp_good, 'FP': fp_good, 'FN': fn_good, 'TN': tn_good}
        },
        'defect': {
            'Accuracy': accuracy_defect,
            'Precision': precision_defect,
            'Recall': recall_defect,
            'Specificity': specificity_defect,
            'Confusion Matrix': {'TP': tp_defect, 'FP': fp_defect, 'FN': fn_defect, 'TN': tn_defect}
        }
    }

# 모델 평가 수행 함수
def evaluate_saved_models(model_names, test_loaders_good, test_loaders_defect, categories, num_classes, output_dir, model_paths):
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

            result = evaluate_model_by_category(
                model,
                dataloader_good=test_loaders_good[category],
                dataloader_defect=test_loaders_defect[category]
            )

            # 결과 저장
            results.append({
                'Model': model_name,
                'Category': category,
                'Good Accuracy': result['good']['Accuracy'],
                'Good Precision': result['good']['Precision'],
                'Good Recall': result['good']['Recall'],
                'Good Specificity': result['good']['Specificity'],
                'Good Confusion Matrix': result['good']['Confusion Matrix'],
                'Defect Accuracy': result['defect']['Accuracy'],
                'Defect Precision': result['defect']['Precision'],
                'Defect Recall': result['defect']['Recall'],
                'Defect Specificity': result['defect']['Specificity'],
                'Defect Confusion Matrix': result['defect']['Confusion Matrix']
            })

    # 평가 결과를 CSV 파일로 저장
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"evaluation_results_{current_time}.csv")
    save_evaluation_results(results, output_file)

# 테스트 데이터 로더 설정
def prepare_test_loaders(categories, test_good_dirs, test_defect_dirs, batch_size):
    test_loaders_good = {}
    test_loaders_defect = {}
    print("Preparing test images...")

    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    for category, good_dir, defect_info in zip(categories, test_good_dirs, test_defect_dirs):
        # Good 데이터 로더
        test_dataset_good = CustomDefectDataset(good_dir, [], transform=test_transform)
        test_loader_good = DataLoader(test_dataset_good, batch_size=batch_size, shuffle=False)
        test_loaders_good[category] = test_loader_good

        # Defect 데이터 로더
        test_dataset_defect = CustomDefectDataset("", defect_info['defects'], transform=test_transform)
        test_loader_defect = DataLoader(test_dataset_defect, batch_size=batch_size, shuffle=False)
        test_loaders_defect[category] = test_loader_defect

    return test_loaders_good, test_loaders_defect

# 평가 결과 저장 함수
def save_evaluation_results(results, output_file):
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Evaluation results saved to {output_file}")

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

# 테스트 데이터 로더 준비 후 모델 평가 수행
test_loaders_good, test_loaders_defect = prepare_test_loaders(categories, test_good_dirs, test_defect_dirs, batch_size)
evaluate_saved_models(model_names, test_loaders_good, test_loaders_defect, categories, num_classes, output_dir, model_paths)
