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


async def delete_file(s3_client, key: str):
    try:
        await s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        print(f"파일 삭제 성공: {key}")
    except Exception as e:
        print(f"삭제 실패: {e}")


async def upload_files(image_list: List[BytesIO]) -> List[str]:
    s3_urls = []

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


async def delete_files(num_of_images: int, key: str):
    async with aioboto3.client(
        's3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_S3_PRIVATE_KEY
    ) as s3_client:
        tasks = []

        for index in range(num_of_images):
            key_url = f"{key}/{index}"
            tasks.append(delete_file(s3_client, key_url))

        await asyncio.gather(*tasks)