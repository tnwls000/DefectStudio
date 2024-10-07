import subprocess

import torch
import torch.cuda

from celery.celery import celery_app


@celery_app.task(name="training", queue="tra_queue")
def training_task(command, output_dir, gpu_device, cost, model):
    try:
        training_process = subprocess.Popen(command)
        training_process.wait()
        torch.cuda.empty_cache()
        return "Training completed"
    except subprocess.CalledProcessError as e:
        return f"Error occurred while executing command: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"