FROM ubuntu:22.04


# 작업 디렉토리를 /app/S11P21S001/ai으로 설정
WORKDIR /app/S11P21S001/ai

# 필요한 파일 복사 (소스코드만 복사)
COPY . .

RUN apt update -y
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.10 python3-pip -y
RUN pip install --upgrade pip

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

RUN pip install -r requirements.txt


# 8000번 포트 노출
EXPOSE 8000

# 5555 포트 (Flower 포트) 노출
EXPOSE 5555

# run.sh 스크립트 실행
CMD ["bash", "run.sh"]

