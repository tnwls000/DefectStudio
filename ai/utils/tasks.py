from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline

from core.config import settings
from utils.celery import celery_app
from utils.scheduler import get_scheduler
from utils.zip import generate_zip_from_images


@celery_app.task(name="generate", queue="gen_queue")
def text_to_image_task(**kwargs):
    model = kwargs["model"]
    scheduler = kwargs.get("scheduler")
    prompt = kwargs["prompt"]
    negative_prompt = kwargs.get("negative_prompt")
    width = kwargs["width"]
    height = kwargs["height"]
    num_inference_steps = kwargs["num_inference_steps"]
    guidance_scale = kwargs["guidance_scale"]
    seed = kwargs["seed"]
    batch_count = kwargs["batch_count"]
    batch_size = kwargs["batch_size"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_dir = settings.OUTPUT_DIR
    model_path = Path(model_dir) / model

    t2i_pipe = StableDiffusionPipeline.from_pretrained(model_path, torch_dtype=torch.float16).to(device)

    if scheduler:
        t2i_pipe.scheduler = get_scheduler(scheduler, t2i_pipe.scheduler.config)

    total_images = batch_size * batch_count
    seeds = [(seed + i) % (2 ** 32) for i in range(total_images)]

    generated_image_list = []

    for i in range(batch_count):
        current_seeds = seeds[i * batch_size: (i + 1) * batch_size]
        generators = [torch.Generator(device=device).manual_seed(s) for s in current_seeds]

        images = t2i_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generators,
            num_images_per_prompt=len(generators),
        ).images

        generated_image_list.extend(images)

    zip_buffer = generate_zip_from_images(generated_image_list)

    return zip_buffer