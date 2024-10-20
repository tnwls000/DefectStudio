#!/bin/bash

# 훈련용 diffusers 수정본
#if [ ! -d "/app/diffusers-fork-defectStudio" ]; then
#    git clone https://github.com/Kimbumsoo99/diffusers-fork-defectStudio.git /app/diffusers-fork-defectStudio
#fi

# 모델 다운로드: 디렉토리가 없을 때만 클론
#if [ ! -d "/app/model/stable-diffusion-2" ]; then
#    git clone https://huggingface.co/stabilityai/stable-diffusion-2 /app/model/stable-diffusion-2
#fi
#
#if [ ! -d "/app/model/stable-diffusion-2-inpainting" ]; then
#    git clone https://huggingface.co/stabilityai/stable-diffusion-2-inpainting /app/model/stable-diffusion-2-inpainting
#fi

# FastAPI 실행
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Celery worker 실행 (2개의 큐)
celery -A workers.celery.celery_app worker --hostname=gen --queues=gen_queue --loglevel=info --pool=threads &
celery -A workers.celery.celery_app worker --hostname=tra --queues=tra_queue --loglevel=info --pool=threads &

# Flower 실행
celery -A workers.celery.celery_app flower --address=0.0.0.0 --port=5555 &

# 컨테이너가 종료되지 않도록 대기
tail -f /dev/null
