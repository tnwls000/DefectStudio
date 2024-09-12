from typing import Optional, List

import requests
from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException

from enums import GPUEnvironment

router = APIRouter(
    prefix="/dreambooth",
)

@router.post("/{gpu_env}")
async def dreambooth(
        gpu_env: GPUEnvironment,
        model: str = Form("stable-diffusion-2", description="초기 모델입니다."),
        revision: str = Form(None, description="모델의 리비전 (선택사항)."),
        variant: str = Form(None, description="모델 파일의 변형 (예: fp16)."),
        tokenizer_name: str = Form(None, description="사전 학습된 토크나이저 이름 또는 경로."),
        # instance_data_dir: str = Form(..., description="학습할 인스턴스 이미지 데이터 폴더 경로. local에서 사용, remote는 images 요청 처리"),
        # class_data_dir: str = Form(None, description="학습할 클래스 이미지 데이터 폴더 경로. local에서 사용, remote는 images 요청 처리"),
        instance_prompt: str = Form(..., description="학습할 인스턴스를 지정하는 프롬프트."),
        class_prompt: str = Form(None, description="클래스 이미지 프롬프트."),
        with_prior_preservation: bool = Form(False, description="사전 보존 손실을 적용할지 여부."),
        prior_loss_weight: float = Form(1.0, description="사전 보존 손실의 가중치."),
        num_class_images: int = Form(100, description="사전 보존 손실을 위한 최소 클래스 이미지 수."),
        seed: int = Form(None, description="재현 가능한 학습을 위한 시드."),
        resolution: int = Form(512, description="학습 및 검증 이미지 해상도."),
        center_crop: bool = Form(False, description="이미지를 중앙에서 자를지 여부."),
        train_text_encoder: bool = Form(False, description="텍스트 인코더를 학습할지 여부."),
        train_batch_size: int = Form(2, description="학습 데이터 로더의 배치 크기."),
        sample_batch_size: int = Form(2, description="샘플링할 이미지의 배치 크기."),
        num_train_epochs: int = Form(30, description="학습할 에폭 수."),
        max_train_steps: int = Form(None, description="학습할 최대 스텝 수."),
        checkpointing_steps: int = Form(500, description="체크포인트를 저장할 스텝 수."),
        checkpoints_total_limit: int = Form(None, description="저장할 체크포인트의 최대 개수."),
        resume_from_checkpoint: str = Form(None, description="이전 체크포인트에서 학습을 재개할지 여부."),
        gradient_accumulation_steps: int = Form(1, description="그래디언트 누적 스텝 수."),
        gradient_checkpointing: bool = Form(False, description="메모리 절약을 위한 그래디언트 체크포인팅."),
        learning_rate: float = Form(5e-6, description="초기 학습률."),
        scale_lr: bool = Form(False, description="GPU 수에 따라 학습률을 스케일링할지 여부."),
        lr_scheduler: str = Form("constant", description="학습률 스케줄러 유형."),
        lr_warmup_steps: int = Form(500, description="학습률 워밍업 스텝 수."),
        lr_num_cycles: int = Form(1, description="`cosine_with_restarts` 스케줄러의 사이클 수."),
        lr_power: float = Form(1.0, description="다항 스케줄러에서의 파워 팩터."),
        use_8bit_adam: bool = Form(False, description="8비트 Adam 옵티마이저 사용 여부."),
        dataloader_num_workers: int = Form(0, description="데이터 로딩에 사용할 워커 수."),
        adam_beta1: float = Form(0.9, description="Adam 옵티마이저의 beta1 값."),
        adam_beta2: float = Form(0.999, description="Adam 옵티마이저의 beta2 값."),
        adam_weight_decay: float = Form(1e-2, description="Adam 옵티마이저의 가중치 감쇠 값."),
        adam_epsilon: float = Form(1e-8, description="Adam 옵티마이저의 epsilon 값."),
        max_grad_norm: float = Form(1.0, description="그래디언트 클리핑의 최대 노름."),
        push_to_hub: bool = Form(False, description="모델을 Hugging Face Model Hub에 푸시할지 여부."),
        hub_token: str = Form(None, description="Model Hub에 푸시할 때 사용할 토큰."),
        hub_model_id: str = Form(None, description="Model Hub와 동기화할 리포지토리 이름."),
        logging_dir: str = Form("logs", description="TensorBoard 로그 디렉터리."),
        allow_tf32: bool = Form(False, description="Ampere GPU에서 TF32 허용 여부."),
        report_to: str = Form("tensorboard", description="결과 및 로그를 보고할 플랫폼."),
        validation_prompt: str = Form(None, description="검증을 위한 프롬프트."),
        num_validation_images: int = Form(4, description="검증 중 생성할 이미지 수."),
        validation_steps: int = Form(100, description="각 검증 실행 사이의 스텝 수."),
        mixed_precision: str = Form(None, description="혼합 정밀도 유형 (fp16 또는 bf16)."),
        prior_generation_precision: str = Form(None, description="사전 생성 정밀도 (fp16, fp32 또는 bf16)."),
        local_rank: int = Form(-1, description="분산 학습을 위한 로컬 랭크."),
        enable_xformers_memory_efficient_attention: bool = Form(False, description="메모리 효율적인 xformers attention 사용."),
        set_grads_to_none: bool = Form(False, description="그래디언트를 None으로 설정하여 메모리 절약."),
        offset_noise: bool = Form(False, description="수정된 노이즈 분포에 대한 파인 튜닝."),
        snr_gamma: float = Form(None, description="손실 재균형을 위한 SNR 가중치 감마 (권장 값: 5.0)."),
        pre_compute_text_embeddings: bool = Form(False, description="텍스트 임베딩을 미리 계산할지 여부."),
        tokenizer_max_length: int = Form(None, description="토크나이저의 최대 길이."),
        text_encoder_use_attention_mask: bool = Form(False, description="텍스트 인코더에 attention mask 사용 여부."),
        skip_save_text_encoder: bool = Form(False, description="텍스트 인코더를 저장하지 않을지 여부."),
        validation_images: str = Form(None, description="검증 시 사용할 이미지 세트."),
        class_labels_conditioning: str = Form(None, description="U-Net에 전달할 클래스 레이블 조건."),
        validation_scheduler: str = Form("DPMSolverMultistepScheduler", description="검증에 사용할 스케줄러."),
        instance_image_list: List[UploadFile] = File(..., description="학습 이미지 파일"),
        class_image_list: List[UploadFile] = File(..., description="학습 범주 이미지 파일")
               ):
    if gpu_env == GPUEnvironment.local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="local 버전은 현재 준비중입니다.")

    num_class_images = len(class_image_list)

    form_data = {
        "model" : model,
        "revision" : revision,
        "variant" : variant,
        "tokenizer_name" : tokenizer_name,
        "instance_prompt" : instance_prompt,
        "class_prompt" : class_prompt,
        "with_prior_preservation" : with_prior_preservation,
        "prior_loss_weight" : prior_loss_weight,
        "num_class_images" : num_class_images,
        "seed" : seed,
        "resolution" : resolution,
        "center_crop" : center_crop,
        "train_text_encoder" : train_text_encoder,
        "train_batch_size" : train_batch_size,
        "sample_batch_size" : sample_batch_size,
        "num_train_epochs" : num_train_epochs,
        "max_train_steps" : max_train_steps,
        "checkpointing_steps" : checkpointing_steps,
        "checkpoints_total_limit" : checkpoints_total_limit,
        "resume_from_checkpoint" : resume_from_checkpoint,
        "gradient_accumulation_steps" : gradient_accumulation_steps,
        "gradient_checkpointing" : gradient_checkpointing,
        "learning_rate" : learning_rate,
        "scale_lr" : scale_lr,
        "lr_scheduler" : lr_scheduler,
        "lr_warmup_steps" : lr_warmup_steps,
        "lr_num_cycles" : lr_num_cycles,
        "lr_power" : lr_power,
        "use_8bit_adam" : use_8bit_adam,
        "dataloader_num_workers" : dataloader_num_workers,
        "adam_beta1" : adam_beta1,
        "adam_beta2" : adam_beta2,
        "adam_weight_decay" : adam_weight_decay,
        "adam_epsilon" : adam_epsilon,
        "max_grad_norm" : max_grad_norm,
        "push_to_hub" : push_to_hub,
        "hub_token" : hub_token,
        "hub_model_id" : hub_model_id,
        "logging_dir" : logging_dir,
        "allow_tf32" : allow_tf32,
        "report_to" : report_to,
        "validation_prompt" : validation_prompt,
        "num_validation_images" : num_validation_images,
        "validation_steps" : validation_steps,
        "mixed_precision" : mixed_precision,
        "prior_generation_precision" : prior_generation_precision,
        "local_rank" : local_rank,
        "enable_xformers_memory_efficient_attention" : enable_xformers_memory_efficient_attention,
        "set_grads_to_none" : set_grads_to_none,
        "offset_noise" : offset_noise,
        "snr_gamma" : snr_gamma,
        "pre_compute_text_embeddings" : pre_compute_text_embeddings,
        "tokenizer_max_length" : tokenizer_max_length,
        "text_encoder_use_attention_mask" : text_encoder_use_attention_mask,
        "skip_save_text_encoder" : skip_save_text_encoder,
        "validation_images" : validation_images,
        "class_labels_conditioning" : class_labels_conditioning,
        "validation_scheduler" : validation_scheduler
    }

    files = []

    files.extend(
        [('instance_image', (image.filename, await image.read(), image.content_type)) for image in instance_image_list])
    files.extend(
        [('class_image', (image.filename, await image.read(), image.content_type)) for image in class_image_list])

    response = requests.post(settings.AI_SERVER_URL + "/training/inpainting", files=files, data=form_data)

    if response.status_code != 200:
        return Response(status_code=response.status_code, content=response.content)

    response_data = response.json()
    train_status = response_data.get("status")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"content": train_status}
    )