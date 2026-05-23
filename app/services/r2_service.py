import boto3
import hashlib
import os
from botocore.config import Config
from decouple import config

R2_ACCOUNT_ID = config("R2_ACCOUNT_ID", default="")
R2_ACCESS_KEY_ID = config("R2_ACCESS_KEY_ID", default="")
R2_SECRET_ACCESS_KEY = config("R2_SECRET_ACCESS_KEY", default="")
R2_PRIVATE_BUCKET = config("R2_PRIVATE_BUCKET", default="100to0lab-private")
R2_PUBLIC_BUCKET = config("R2_PUBLIC_BUCKET", default="100to0lab-public")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
    return _client


def upload_file(file_bytes: bytes, key: str, content_type: str, bucket: str = R2_PRIVATE_BUCKET) -> str:
    get_client().put_object(
        Bucket=bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return key


def get_presigned_download_url(key: str, bucket: str = R2_PRIVATE_BUCKET, expires_in: int = 3600) -> str:
    return get_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def delete_file(key: str, bucket: str = R2_PRIVATE_BUCKET) -> None:
    get_client().delete_object(Bucket=bucket, Key=key)


def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()
