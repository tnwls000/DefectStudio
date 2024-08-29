from config import settings
from io import BytesIO
from typing import List
import aioboto3
import asyncio

s3_client = aioboto3.client(
    "s3",
    aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_S3_PRIVATE_KEY
)


async def upload_file(s3_client, image_io: BytesIO, key: str) -> str:
    image_io.seek(0)
    try:
        await s3_client.upload_fileobj(image_io, settings.AWS_S3_BUCKET, key)
        s3_url = f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/{key}"
        return s3_url
    except Exception as e:
        print(f"업로드 실패: {e}")
        return None


async def upload_files(image_list: List[BytesIO]) -> List[str]:
    s3_urls = []

    # 비동기적으로 생성된 S3 클라이언트 객체, 해당 블록이 끝나면 s3_client는 자동으로 정리
    async with aioboto3.client(
        's3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_S3_PRIVATE_KEY
    ) as s3_client:
        tasks = []
        for index, image_io in enumerate(image_list):
            key = f"file_name_{index}.jpg"
            tasks.append(upload_file(s3_client, image_io, key))

        s3_urls = await asyncio.gather(*tasks)

    return [url for url in s3_urls if url is not None]
