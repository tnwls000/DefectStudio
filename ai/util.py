import boto3
from config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_S3_PRIVATE_KEY
)
