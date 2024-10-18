#!/bin/bash



# 가상환경이 마운트된 경로에서 가상환경 활성화
echo "Activating virtual environment..."
if [ -d "/app/venv/bin" ]; then
    source /app/venv/bin/activate
    echo "Virtual environment activated."
else
    echo "Virtual environment not found!"
    python3 -m venv /app/venv
    source /app/venv/bin/activate
#    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
#    pip install nvidia-cudnn-cu11==8.9.2.26
#    pip install -r requirements.txt
fi

#if [ -d "/app/model" ]; then
#    git clone https://huggingface.co/stabilityai/stable-diffusion-2
#    git clone https://huggingface.co/stabilityai/stable-diffusion-2-inpainting
#if


# FastAPI 실행
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000
