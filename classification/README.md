### train
train 코드들은 기본적으로 모든 카테고리를 하나의 good과 defect로 학습시켰습니다.  
지표로 사용한 모델 학습에 사용된 코드는 train10, train12 입니다.  
차이점
- train10의 경우 모든 카테고리를 하나로 모델 학습
- train12의 경우 각 카테고리별로 모델 학습

학습 시 epoch 별 loss, accuracy 를 측정하고 그래프를 이미지로 저장합니다.  

### evaluation 
평가는 학습시킨 데이터셋에 따라 맞춰서 평가코드를 수정했습니다.  
evalutaion7이 이번 평가지표로 삼은 평가 코드입니다.    
평가 결과를 accuracy, confusion matrix 등을 csv로 저장합니다.  

### results
각 모델(Network)이 훈련된 결과와 평가한 결과를 저장하는 디렉터리

### generation image
gen_data 폴더에는 이미지를 생성하는 코드가 작성되어 있습니다.  
inpaint.py를 사용했습니다.  
기본적으로 inpainting을 사용하여 이미지를 생성합니다.  
directory
- input_images: inpainting 할 원본 이미지와 마스크 이미지를 저장하는 디렉터리
- output_images: inpainting 후 이미지를 저장하는 디렉터리
- model: inpainting에 사용될 stable-diffusion-2-inpainting 기반 모델을 저장하는 디렉터리

---
### MVTec AD evaluation
MVTec AD 평가 코드를 실행시키는 명령어

싱글 콘셉
```
python evaluate_experiment.py ^
  --dataset_base_dir "J:\conductzero\dataset\mvtec_anomaly_detection" ^
  --anomaly_maps_dir "G:\Project\S11P21S001\ai\api\routes\classification\results\20204\anomaly_maps\20240926223321" ^
  --output_dir "G:\Project\S11P21S001\ai\api\routes\classification\anomaly_maps\20240926223321\metrics" ^
  --pro_integration_limit 0.3
```

멀티 콘셉
experiment_configs.json을 형식에 맞춰 작성해야합니다.
```
python evaluate_multiple_experiments.py ^
--experiment_configs "J:\conductzero\project\be\S11P21S001\ai\classification\experiment_configs.json" ^
--dataset_base_dir "J:\conductzero\dataset\mvtec_anomaly_detection" ^
--output_dir "G:\Project\S11P21S001\ai\api\routes\classification\results\20240926234423\anomaly_maps\20240927002529\metrics" ^
--pro_integration_limit 0.3 ^
--dry_run False
```