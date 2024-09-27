from datetime import datetime
from io import BytesIO
from typing import List

import aioboto3
from PIL import Image
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from core.config import settings


async def upload_files(image_list: List[BytesIO]) -> List[str]:
    s3_urls = []
    session = aioboto3.Session()
    async with session.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_S3_SECRET_KEY
    ) as s3_client:

        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d")
        formatted_time = now.strftime("%H%M%S%f")

        for index, image_stream in enumerate(image_list):
            image_key = f"{formatted_date}/{formatted_time}/{index + 1}"
            image_stream.seek(0)

            url = await upload_file(s3_client, image_stream, image_key)
            if url:
                s3_urls.append(url)
    return s3_urls

async def delete_files(num_of_images: int, key: str):
    session = aioboto3.Session()
    async with session.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_S3_SECRET_KEY
    ) as s3_client:

        for index in range(num_of_images):
            key_url = f"{key}/{index + 1}.jpeg"
            await delete_file(s3_client, key_url)


async def upload_file(s3_client, image_stream: BytesIO, key: str) -> str:
    image_stream.seek(0)
    image = Image.open(image_stream)
    format = image.format.lower()
    try:
        image_stream.seek(0)
        await s3_client.upload_fileobj(
            image_stream,
            settings.AWS_S3_BUCKET,
            f"{key}.{format}",
            ExtraArgs={
                'ContentType': 'image/jpeg',
                'ContentDisposition': 'inline'
            }
        )
        s3_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION_STATIC}.amazonaws.com/{key}.jpeg"
        return s3_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {e}")


async def delete_file(s3_client, key: str):
    try:
        s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"삭제 실패: {e}")