import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from datetime import datetime
import numpy as np
from PIL import Image
import pandas as pd
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from custom_dataset import CustomDefectDataset, initialize_model  # 필요한 함수 및 클래스 임포트
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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 평가 결과 저장 함수
# 평가 결과 저장 함수 수정
def save_evaluation_results(results, output_file, save_additional_format=False):
    import pandas as pd

    # 결과를 데이터프레임으로 변환
    df = pd.DataFrame(results)

    # 만약 'ROC-AUC' 또는 다른 열이 없을 경우 'N/A'로 채움
    for column in ['ROC-AUC', 'Average Precision', 'Accuracy']:
        if column not in df.columns:
            df[column] = 'N/A'

    df.to_csv(output_file, index=False)
    print(f"Evaluation results saved to {output_file}")

    if save_additional_format:
        formatted_results = []
        categories = df['Category'].unique()
        for category in categories:
            category_results = df[df['Category'] == category]
            for index, row in category_results.iterrows():
                formatted_results.append({
                    'Category': category,
                    'Model': row['Model'],
                    'ROC-AUC': row['ROC-AUC'] if row['ROC-AUC'] != 'N/A' else 'N/A',
                    'Average Precision': row['Average Precision'] if row['Average Precision'] != 'N/A' else 'N/A',
                    'Accuracy': row['Accuracy']
                })

        # 새로운 데이터프레임 생성 및 저장
        formatted_df = pd.DataFrame(formatted_results)
        additional_output_file = output_file.replace(".csv", "_category_comparison.csv")
        formatted_df.to_csv(additional_output_file, index=False)
        print(f"Additional formatted evaluation results saved to {additional_output_file}")



# 평가 함수 정의 (good, defect 데이터 각각 나누어 평가)
def evaluate_model_by_category(model, dataloader_good, dataloader_defect):
    model.eval()

    def evaluate_single_category(dataloader, label_value):
        all_labels = []
        all_preds = []
        running_corrects = 0
        total_samples = 0

        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                probs = torch.softmax(outputs, dim=1)
                preds = torch.argmax(probs, dim=1)

                # 실제 label을 전부 label_value로 설정 (good=0, defect=1)
                all_labels.extend([label_value] * len(labels))
                all_preds.extend(probs[:, 1].cpu().numpy())

                running_corrects += torch.sum(preds == labels.data)
                total_samples += labels.size(0)

        accuracy = running_corrects.double() / total_samples

        # ROC AUC는 두 클래스가 있을 때만 계산 가능
        if len(np.unique(all_labels)) > 1:
            auc_score = roc_auc_score(all_labels, all_preds)
            precision, recall, _ = precision_recall_curve(all_labels, all_preds)
            average_precision = auc(recall, precision)
        else:
            auc_score = None  # AUC 점수 계산 불가
            average_precision = None

        return auc_score, average_precision, accuracy.item()

    # Good 데이터셋 평가
    print("Evaluating Good images...")
    auc_score_good, average_precision_good, accuracy_good = evaluate_single_category(dataloader_good, label_value=0)
    if auc_score_good is None:
        print(f"Good Images - AUC Score not defined (only one class present), ACC: {accuracy_good:.4f}")
    else:
        print(f"Good Images - ROC-AUC: {auc_score_good:.4f}, AP: {average_precision_good:.4f}, ACC: {accuracy_good:.4f}")

    # Defect 데이터셋 평가
    print("Evaluating Defect images...")
    auc_score_defect, average_precision_defect, accuracy_defect = evaluate_single_category(dataloader_defect, label_value=1)
    if auc_score_defect is None:
        print(f"Defect Images - AUC Score not defined (only one class present), ACC: {accuracy_defect:.4f}")
    else:
        print(f"Defect Images - ROC-AUC: {auc_score_defect:.4f}, AP: {average_precision_defect:.4f}, ACC: {accuracy_defect:.4f}")

    return {
        'good': {
            'ROC-AUC': auc_score_good,
            'Average Precision': average_precision_good,
            'Accuracy': accuracy_good
        },
        'defect': {
            'ROC-AUC': auc_score_defect,
            'Average Precision': average_precision_defect,
            'Accuracy': accuracy_defect
        }
    }



# 모델 평가 수행 함수 (good과 defect 나눠서 평가)
def evaluate_all_categories(model_names, test_loaders_good, test_loaders_defect, categories, num_classes, output_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = []

    for model_name in model_names:
        print(f"=== Evaluating {model_name} ===")

        # 사전 학습된 모델 경로를 전달할 수 있도록 수정
        pretrained_path = None
        if pretrained_paths is not None and model_name in pretrained_paths:
            pretrained_path = pretrained_paths[model_name]

        model = initialize_model(model_name, num_classes, load_from=pretrained_path)
        # 모델 초기화
        # model = initialize_model(model_name, num_classes)
        model = model.to(device)

        # 각 카테고리에 대해 모델 평가
        for category in categories:
            print(f"Evaluating {category} with {model_name}")

            # good, defect 각각에 대해 평가 수행
            result = evaluate_model_by_category(
                model,
                dataloader_good=test_loaders_good[category],
                dataloader_defect=test_loaders_defect[category]
            )

            # 결과 저장
            results.append({
                'Model': model_name,
                'Category': category,
                'Good ROC-AUC': result['good']['ROC-AUC'],
                'Good Average Precision': result['good']['Average Precision'],
                'Good Accuracy': result['good']['Accuracy'],
                'Defect ROC-AUC': result['defect']['ROC-AUC'],
                'Defect Average Precision': result['defect']['Average Precision'],
                'Defect Accuracy': result['defect']['Accuracy']
            })

    # 평가 결과를 CSV 파일로 저장
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"evaluation_results_{current_time}.csv")
    save_evaluation_results(results, output_file, save_additional_format=True)


# 테스트 데이터 로더 설정 (good과 defect를 분리)
def prepare_test_loaders(test_good_dirs, test_defect_dirs, categories, batch_size):
    test_loaders_good = {}
    test_loaders_defect = {}

    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print("Preparing test images...")
    for category, good_dir, defect_info in zip(categories, test_good_dirs, test_defect_dirs):

        # 각 카테고리의 good 데이터 로더
        test_dataset_good = CustomDefectDataset(good_dir, [], transform=test_transform)
        test_loader_good = DataLoader(test_dataset_good, batch_size=batch_size, shuffle=False)
        test_loaders_good[category] = test_loader_good

        # 각 카테고리의 defect 데이터 로더
        test_dataset_defect = CustomDefectDataset("", defect_info['defects'], transform=test_transform)
        test_loader_defect = DataLoader(test_dataset_defect, batch_size=batch_size, shuffle=False)
        test_loaders_defect[category] = test_loader_defect

    return test_loaders_good, test_loaders_defect


if __name__ == "__main__":
    # 기본 데이터셋 경로 설정 및 하이퍼파라미터
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

    # 모델 이름 리스트
    model_names = ["efficientnet_v2_s", "resnet34", "convnext_tiny", "mobilenet_v3_small"]

    base_model_dir = r"J:\conductzero\project\be\S11P21S001\ai\classification\results\20240927114147"
    model_type = "best"
    pretrained_paths = {
        "efficientnet_v2_s": f"{base_model_dir}/efficientnet_v2_s_{model_type}_model.pth",
        "resnet34": f"{base_model_dir}/resnet34_{model_type}_model.pth",
        # "convnext_tiny": f"{base_model_dir}/convnext_tiny_{model_type}_model.pth",
        "mobilenet_v3_small": f"{base_model_dir}/mobilenet_v3_small_{model_type}_model.pth"
    }


    # 하이퍼파라미터
    batch_size = 16
    num_classes = 2
    output_dir = 'results'

    # 테스트 데이터 로더 준비
    test_loaders_good, test_loaders_defect = prepare_test_loaders(test_good_dirs, test_defect_dirs, categories, batch_size)

    # 모델 평가 수행
    evaluate_all_categories(model_names, test_loaders_good, test_loaders_defect, categories, num_classes, output_dir)
