from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
import os
import subprocess

# 필요 env
'''
OUTPUT_DIR=model, class, instance image -> model load, model save, class_dir save, instance_dir save
DIFFUSERS_TRAIN_PATH= diffusers git repo path
'''

router = APIRouter(
    prefix="/dreambooth",
)

training_process = None
log_file_path = None

@router.post("")
async def train_dreambooth(request: Request, background_tasks: BackgroundTasks):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    # global training_process, log_file_path

    form = await request.form()

    try:
        # remote 환경
        base_output_dir = os.getenv("OUTPUT_DIR")  # /checkpoints

        # 모델 학습 파라미터
        # 모델 및 토크나이저 설정
        pretrained_model_name_or_path = form.get("model_name")
        revision = form.get("revision")
        variant = form.get("variant")
        tokenizer_name = form.get("tokenizer_name")
        instance_data_dir = form.get("instance_data_dir")
        class_data_dir = form.get("class_data_dir")

        # 데이터 및 프롬프트 설정
        instance_prompt = form.get("instance_prompt")
        class_prompt = form.get("class_prompt")
        num_class_images = form.get("num_class_images")
        center_crop = form.get("center_crop")

        # 가중치
        with_prior_preservation = form.get("with_prior_preservation")
        prior_loss_weight = form.get("prior_loss_weight", 1.0)

        # 학습 설정
        seed = form.get("seed")
        resolution = form.get("resolution", 512)
        train_text_encoder = form.get("train_text_encoder")
        train_batch_size = form.get("train_batch_size", 2)
        sample_batch_size = form.get("sample_batch_size")
        num_train_epochs = form.get("num_train_epochs")
        max_train_steps = form.get("max_train_steps")
        learning_rate = form.get("learning_rate", 1e-6)
        offset_noise = form.get("offset_noise")

        # 검증 및 체크포인트 설정
        checkpointing_steps = form.get("checkpointing_steps")
        checkpoints_total_limit = form.get("checkpoints_total_limit")
        resume_from_checkpoint = form.get("resume_from_checkpoint")
        validation_prompt = form.get("validation_prompt")
        num_validation_images = form.get("num_validation_images")
        validation_steps = form.get("validation_steps")
        validation_images = form.get("validation_images")
        validation_scheduler = form.get("validation_scheduler")

        # 최적화 및 정밀도 설정
        use_8bit_adam = form.get("use_8bit_adam")
        adam_beta1 = form.get("adam_beta1")
        adam_weight_decay = form.get("adam_weight_decay")
        adam_beta2 = form.get("adam_beta2")
        adam_epsilon = form.get("adam_epsilon")
        max_grad_norm = form.get("max_grad_norm")

        # 데이터 증강 및 메모리 관리
        gradient_accumulation_steps = form.get("gradient_accumulation_steps", 2)
        gradient_checkpointing = form.get("gradient_checkpointing")
        enable_xformers_memory_efficient_attention = form.get("enable_xformers_memory_efficient_attention")
        set_grads_to_none = form.get("set_grads_to_none")

        # 기타 설정
        # TODO 후에 local gpu server 사용
        output_dir = form.get("output_dir")
        scale_lr = form.get("scale_lr")
        lr_scheduler = form.get("lr_scheduler", "constant")
        lr_warmup_steps = form.get("lr_warmup_steps", "0")
        lr_num_cycles = form.get("lr_num_cycles")
        lr_power = form.get("lr_power")
        dataloader_num_workers = form.get("dataloader_num_workers")
        push_to_hub = form.get("push_to_hub")
        hub_token = form.get("hub_token")
        hub_model_id = form.get("hub_model_id")
        logging_dir = form.get("logging_dir")
        allow_tf32 = form.get("allow_tf32")
        report_to = form.get("report_to")
        mixed_precision = form.get("mixed_precision")
        prior_generation_precision = form.get("prior_generation_precision")
        local_rank = form.get("local_rank")
        snr_gamma = form.get("snr_gamma")
        pre_compute_text_embeddings = form.get("pre_compute_text_embeddings")
        tokenizer_max_length = form.get("tokenizer_max_length")
        text_encoder_use_attention_mask = form.get("text_encoder_use_attention_mask")
        skip_save_text_encoder = form.get("skip_save_text_encoder")
        class_labels_conditioning = form.get("class_labels_conditioning")

        # 이외 파라미터
        member_id = form.get("member_id")
        train_model_name = form.get("train_model_name")
        log_epochs = form.get("log_epochs")

        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        instance_images = form.getlist("instance_images")
        class_images = form.getlist("class_images")

        # model_name(model_name) : Base Model(local에 stabilityai/stable-diffusion-2 Save)
        # instance_data(instance_dir) : instance image requests (!required)
        # class_data(class_dir) : class image requests (!required)
        # output_dir : f"base_path + {member_id}/{model_name}" -> model_name 검증 로직?
        # instance_prompt : requests (!required)
        # class_prompt : requests (!required)
        # batch_size : requests (!required, default : 2)
        # learning_rate : requests (default: 1e-6)
        # num_class_images : class_images 개수
        # num_train_epochs : requests (default: 30)

        output_dir = os.path.join(base_output_dir, f"{member_id}", f"{train_model_name}")
        os.makedirs(output_dir, exist_ok=True)

        instance_dir = os.path.join(base_output_dir, f"{member_id}", "instance_images")
        class_dir = os.path.join(base_output_dir, f"{member_id}", "class_images")
        os.makedirs(instance_dir, exist_ok=True)
        os.makedirs(class_dir, exist_ok=True)

        if ("stable-diffusion-2" == pretrained_model_name_or_path):
            pretrained_model_name_or_path = os.path.join(base_output_dir, pretrained_model_name_or_path)
        else:
            pretrained_model_name_or_path = os.path.join(base_output_dir, f"{member_id}", pretrained_model_name_or_path)

        # 인스턴스 이미지 저장
        for image in instance_images:
            with open(os.path.join(instance_dir, image.filename), "wb") as f:
                f.write(await image.read())

        # 클래스 이미지 저장
        for image in class_images:
            with open(os.path.join(class_dir, image.filename), "wb") as f:
                f.write(await image.read())

        project_root = os.getenv('DIFFUSERS_TRAIN_PATH')
        train_script = os.path.join(project_root, "dreambooth/train_dreambooth.py")

        # TODO LOG 관련 기능 미사용 중
        # log_file_path = os.path.join(base_output_dir, f"{member_id}", "training.log")

        # 필수 파라미터 추가
        command = [
            "accelerate", "launch", train_script,
            "--pretrained_model_name_or_path", pretrained_model_name_or_path,
            "--instance_data_dir", instance_dir,
            "--class_data_dir", class_dir,
            "--output_dir", output_dir,
            "--resolution", resolution,
            "--train_batch_size", train_batch_size,
            "--learning_rate", learning_rate,
            "--num_class_images", num_class_images,
            # "--logging_epoch", "True",
            "--num_train_epochs", num_train_epochs
        ]

        # 필수 파라미터?
        if not with_prior_preservation:
            command.extend(["--with_prior_preservation"])
        command.extend(["--prior_loss_weight", prior_loss_weight])
        command.extend(["--instance_prompt", instance_prompt])
        command.extend(["--class_prompt", class_prompt])
        command.extend(["--gradient_accumulation_steps", gradient_accumulation_steps])
        command.extend(["--gradient_checkpointing"])
        command.extend(["--use_8bit_adam"])
        command.extend(["--lr_scheduler", lr_scheduler])
        command.extend(["--lr_warmup_steps", lr_warmup_steps])

        # 선택적 파라미터 추가
        if not revision:
            command.extend(["--revision", revision])
        if not variant:
            command.extend(["--variant", variant])
        if not tokenizer_name:
            command.extend(["--tokenizer_name", tokenizer_name])
        if not instance_data_dir:
            command.extend(["--instance_data_dir", instance_data_dir])
        if not class_data_dir:
            command.extend(["--class_data_dir", class_data_dir])
        if not center_crop:
            command.extend(["--center_crop", center_crop])
        if not seed:
            command.extend(["--seed", seed])
        if not train_text_encoder:
            command.extend(["--train_text_encoder", train_text_encoder])
        if not sample_batch_size:
            command.extend(["--sample_batch_size", sample_batch_size])
        if not max_train_steps:
            command.extend(["--max_train_steps", max_train_steps])
        if not offset_noise:
            command.extend(["--offset_noise", offset_noise])
        if not checkpointing_steps:
            command.extend(["--checkpointing_steps", checkpointing_steps])
        if not checkpoints_total_limit:
            command.extend(["--checkpoints_total_limit", checkpoints_total_limit])
        if not resume_from_checkpoint:
            command.extend(["--resume_from_checkpoint", resume_from_checkpoint])
        if not validation_prompt:
            command.extend(["--validation_prompt", validation_prompt])
        if not num_validation_images:
            command.extend(["--num_validation_images", num_validation_images])
        if not validation_steps:
            command.extend(["--validation_steps", validation_steps])
        if not validation_images:
            command.extend(["--validation_images", validation_images])
        if not validation_scheduler:
            command.extend(["--validation_scheduler", validation_scheduler])
        if not use_8bit_adam:
            command.extend(["--use_8bit_adam", use_8bit_adam])
        if not adam_beta1:
            command.extend(["--adam_beta1", adam_beta1])
        if not adam_weight_decay:
            command.extend(["--adam_weight_decay", adam_weight_decay])
        if not adam_beta2:
            command.extend(["--adam_beta2", adam_beta2])
        if not adam_epsilon:
            command.extend(["--adam_epsilon", adam_epsilon])
        if not max_grad_norm:
            command.extend(["--max_grad_norm", max_grad_norm])
        if not gradient_checkpointing:
            command.extend(["--gradient_checkpointing", gradient_checkpointing])
        if not enable_xformers_memory_efficient_attention:
            command.extend(["--enable_xformers_memory_efficient_attention", enable_xformers_memory_efficient_attention])
        if not set_grads_to_none:
            command.extend(["--set_grads_to_none", set_grads_to_none])
        '''
        Local 사용 시 사용 고려
        if not output_dir:
            command.extend(["--output_dir", output_dir])
        '''
        if not scale_lr:
            command.extend(["--scale_lr", scale_lr])
        if not lr_num_cycles:
            command.extend(["--lr_num_cycles", lr_num_cycles])
        if not lr_power:
            command.extend(["--lr_power", lr_power])
        if not dataloader_num_workers:
            command.extend(["--dataloader_num_workers", dataloader_num_workers])
        if not push_to_hub:
            command.extend(["--push_to_hub", push_to_hub])
        if not hub_token:
            command.extend(["--hub_token", hub_token])
        if not hub_model_id:
            command.extend(["--hub_model_id", hub_model_id])
        if not logging_dir:
            command.extend(["--logging_dir", logging_dir])
        if not allow_tf32:
            command.extend(["--allow_tf32", allow_tf32])
        if not report_to:
            command.extend(["--report_to", report_to])
        if not mixed_precision:
            command.extend(["--mixed_precision", mixed_precision])
        if not prior_generation_precision:
            command.extend(["--prior_generation_precision", prior_generation_precision])
        if not local_rank:
            command.extend(["--local_rank", local_rank])
        if not snr_gamma:
            command.extend(["--snr_gamma", snr_gamma])
        if not pre_compute_text_embeddings:
            command.extend(["--pre_compute_text_embeddings", pre_compute_text_embeddings])
        if not tokenizer_max_length:
            command.extend(["--tokenizer_max_length", tokenizer_max_length])
        if not text_encoder_use_attention_mask:
            command.extend(["--text_encoder_use_attention_mask", text_encoder_use_attention_mask])
        if not skip_save_text_encoder:
            command.extend(["--skip_save_text_encoder", skip_save_text_encoder])
        if not class_labels_conditioning:
            command.extend(["--class_labels_conditioning", class_labels_conditioning])

        # Custom Command
        if not log_epochs:
            command.extend(["--log_epochs", log_epochs])

        if os.name == 'nt':
            command = ['cmd', '/c'] + command

        background_tasks.add_task(run_training, command)
        return {"status": "Training started successfully", "output_dir": output_dir}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_training(command):
    global training_process
    training_process = subprocess.Popen(command)
    training_process.wait()


# 향후 status 확인 필요 시 사용
@router.get("/training_status/")
async def training_status():
    global training_process, log_file_path

    if training_process is None:
        raise HTTPException(status_code=400, detail="Training has not started yet.")

    poll = training_process.poll()
    if poll is None:
        status = "Training is still running."
    else:
        status = "Training has completed."

    log_content = ""
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            log_content = log_file.read()

    return {
        "status": status,
        "log": log_content
    }
