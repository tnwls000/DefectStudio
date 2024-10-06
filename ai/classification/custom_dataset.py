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


class CustomDefectDataset(Dataset):
    def __init__(self, good_dir, defect_dirs, transform=None):
        self.good_dir = good_dir
        self.defect_dirs = defect_dirs
        self.transform = transform
        self.image_paths = []
        self.labels = []

        # 카테고리명 추출 (good_dir의 두 단계 상위 폴더)
        self.category = os.path.basename(os.path.dirname(os.path.dirname(good_dir)))
        self.image_counts = {'good': 0, 'defect': 0}  # 이미지 개수 저장용

        # good 이미지 로드
        if os.path.exists(good_dir):
            good_images = [os.path.join(good_dir, fname) for fname in os.listdir(good_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.image_paths.extend([(img, 0) for img in good_images])
            self.image_counts['good'] += len(good_images)  # good 이미지 개수 추가

        # defect 이미지 로드
        for defect_dir in defect_dirs:
            if os.path.exists(defect_dir):
                defect_images = [os.path.join(defect_dir, fname) for fname in os.listdir(defect_dir) if fname.lower().endswith(('.png', '.jpg', '.jpeg'))]
                self.image_paths.extend([(img, 1) for img in defect_images])
                self.image_counts['defect'] += len(defect_images)  # defect 이미지 개수 추가

        # 카테고리별 이미지 개수 출력
        print(f"Category: {self.category} - Good Images: {self.image_counts['good']}, Defect Images: {self.image_counts['defect']}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path, label = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, label



# 모델 초기화 함수
# 기존 코드에서 모델을 초기화하는 부분을 수정
def initialize_model(model_name, num_classes, pretrained=True, load_from=None):
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

    # 학습된 모델을 불러오는 부분 추가
    if load_from is not None and os.path.exists(load_from):
        print(f"Loading model weights from {load_from}")
        model.load_state_dict(torch.load(load_from))
    return model