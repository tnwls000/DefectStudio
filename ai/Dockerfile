# 베이스 이미지: Python 3.10
#FROM python:3.10.6
FROM ubuntu:20.04

RUN apt-get update -y
RUN apt-get upgrade -y
#RUN apt-get install -y build-essential binutils libtool make gcc g++ openjdk-8-jdk git dos2unix vim wget
RUN apt-get install -y build-essential wget vim dos2unix
RUN apt-get install -y zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget software-properties-common
RUN apt-get install -y ocl-icd-opencl-dev
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update -y
RUN apt-get install -y python3.10
RUN apt-get install -y python3.10-venv

# 작업 디렉토리를 /app/S11P21S001/ai으로 설정
WORKDIR /app/S11P21S001/ai

# 필요한 파일 복사 (소스코드만 복사)
COPY . .

#RUN python3 -m venv /app/venv && \
#    chmod +x /app/venv/bin/activate && \
#    /app/venv/bin/activate
#    python -m pip install --upgrade pip && \
#    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
#    pip install nvidia-cudnn-cu11==8.9.2.26 && \
#    pip install -r requirements.txt

# 8000번 포트 노출
EXPOSE 8000

# FastAPI 애플리케이션 실행
#CMD ["/app/venv/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

