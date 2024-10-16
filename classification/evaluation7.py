import os
import torch
import torch.nn as nn
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from sklearn.metrics import confusion_matrix, precision_score, recall_score, accuracy_score
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
            self.image_paths.extend(good_images)
            self.labels.extend([0] * len(good_images))
            self.image_counts['good'] += len(good_images)

        # defect 이미지 로드
        for defect_dir in defect_dirs:
            if os.path.exists(defect_dir):
                defect_images = [os.path.join(defect_dir, fname) for fname in os.listdir(defect_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.image_paths.extend(defect_images)
                self.labels.extend([1] * len(defect_images))
                self.image_counts['defect'] += len(defect_images)

        print(f"Good Images: {self.image_counts['good']}, Defect Images: {self.image_counts['defect']}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
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

    # 학습된 모델을 불러오는 부분 추가
    # if load_from is not None and os.path.exists(load_from):
    #     print(f"Loading model weights from {load_from}")
    #     model.load_state_dict(torch.load(load_from))


    return model


# 평가 함수 정의 (Confusion Matrix 포함)
def evaluate_model_with_confusion_matrix(model, dataloader):
    model.eval()
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

    # Confusion Matrix 계산
    cm = confusion_matrix(all_labels, all_preds)
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='binary')
    recall = recall_score(all_labels, all_preds, average='binary')

    return accuracy, precision, recall, cm


# 모델 평가 수행 함수
def evaluate_saved_models_with_confusion_matrix(model_names, test_loaders_dict, num_classes, output_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 최종 CSV 파일에 저장할 데이터를 모으기 위한 리스트
    all_results = []
    model_type = "full"
    model_dir = "20241007234017"

    for model_name in model_names:
        print(f"=== Evaluating {model_name} ===")



        # 각 카테고리에 대해 평가 수행
        for category, test_loader in test_loaders_dict.items():
            model_paths = {
                "efficientnet_v2_s": fr"results\{model_dir}\efficientnet_v2_s_{model_type}_model_{category}.pth",
                "resnet34": fr"results\{model_dir}\resnet34_{model_type}_model_{category}.pth",
                "mobilenet_v3_small": fr"results\{model_dir}\mobilenet_v3_small_{model_type}_model_{category}.pth"
            }

            model_path = model_paths.get(model_name)
            if not model_path:
                print(f"No saved model found for {model_name}. Skipping...")
                continue

            model = initialize_model(model_name, num_classes, load_from=model_path)
            model = model.to(device)

            print(f"Evaluating category: {category}")
            # Confusion Matrix 및 성능 지표 평가
            accuracy, precision, recall, cm = evaluate_model_with_confusion_matrix(model, test_loader)

            # 카테고리와 모델별 결과 추가
            all_results.append({
                'Model': model_name,
                'Category': category,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'Confusion Matrix': cm.tolist()  # Confusion Matrix를 리스트로 변환하여 저장
            })

    # 최종 결과를 하나의 CSV 파일로 저장
    results_df = pd.DataFrame(all_results)
    results_csv_path = os.path.join(output_dir, f'{model_dir}_{model_type}_{datetime.now().strftime("%Y%m%d%H%M%S")}_all_evaluation_results.csv')
    results_df.to_csv(results_csv_path, index=False)

    print(f"All results saved to {results_csv_path}")


# 테스트 데이터 로더 설정 함수
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


if __name__ == '__main__':
    # 하이퍼파라미터 설정 및 모델 경로 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    base_dir = r'J:\conductzero\dataset\mvtec_anomaly_detection_init'
    #categories = ['bottle', 'cable', 'capsule', 'carpet', 'grid', 'hazelnut', 'leather', 'metal_nut', 'pill', 'screw', 'tile', 'toothbrush', 'transistor', 'wood', 'zipper']
    # categories = ['bottle', 'cable', 'capsule', 'hazelnut', 'metal_nut','transistor']
    categories = ['metal_nut']

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

    batch_size = 16
    num_classes = 2
    output_dir = "results"

    # 테스트 데이터 로더 준비
    test_loaders_dict = prepare_test_loaders(categories, test_good_dirs, test_defect_dirs, batch_size)

    # 모델 평가 수행 (모델별로 순회하면서 카테고리별로 평가)
    evaluate_saved_models_with_confusion_matrix(model_names, test_loaders_dict, num_classes, output_dir)
