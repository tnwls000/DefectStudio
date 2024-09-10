from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException, status, Response
from starlette.responses import JSONResponse
import torch
import nvidia_smi

router = APIRouter()


@router.get("/health")
async def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"health": "good"})


@router.get("/cuda_available")
async def cuda_available():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"cuda_available": torch.cuda.is_available()})

@router.get("/cuda_usage")
async def cuda_usage():
    # NVML 초기화
    nvidia_smi.nvmlInit()

    # GPU 장치 수 가져오기
    deviceCount = nvidia_smi.nvmlDeviceGetCount()

    # 결과를 저장할 리스트
    gpu_info = []

    # 각 GPU의 메모리 정보 조회
    for i in range(deviceCount):
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
        info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        name = nvidia_smi.nvmlDeviceGetName(handle).decode("utf-8")  # GPU 이름을 문자열로 변환
        free_memory = info.free / (1024 ** 2)  # 여유 메모리(MB)
        used_memory = info.used / (1024 ** 2)  # 사용 중인 메모리(MB)
        total_memory = info.total / (1024 ** 2)  # 총 메모리(MB)
        used_memory_percentage = 100 * info.used / info.total  # 사용 메모리 비율 (%)
        free_memory_percentage = 100 * info.free / info.total  # 여유 메모리 비율 (%)

        # 각 GPU의 정보 저장
        gpu_info.append({
            "GPU num": i,
            "GPU name": name,
            "Total memory (MB)": total_memory,
            "Free memory (MB)": free_memory,
            "Used memory (MB)": used_memory,
            "Free memory (%)": free_memory_percentage,
            "Used memory (%)": used_memory_percentage,
        })

    # NVML 종료
    nvidia_smi.nvmlShutdown()

    # JSON 응답 반환
    return JSONResponse(status_code=status.HTTP_200_OK, content={"gpu_info": gpu_info})