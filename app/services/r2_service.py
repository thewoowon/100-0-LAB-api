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
R2_PUBLIC_URL = config("R2_PUBLIC_URL", default="")  # e.g. https://pub-xxx.r2.dev

_client = None


def is_configured() -> bool:
    return bool(R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY)


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
    if not is_configured():
        return key  # 로컬 개발 환경: 업로드 건너뜀
    get_client().put_object(
        Bucket=bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return key


def get_presigned_download_url(key: str, bucket: str = R2_PRIVATE_BUCKET, expires_in: int = 3600) -> str:
    if not is_configured():
        return ""  # 로컬 개발 환경
    return get_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def delete_file(key: str, bucket: str = R2_PRIVATE_BUCKET) -> None:
    if not is_configured():
        return
    get_client().delete_object(Bucket=bucket, Key=key)


def copy_to_public(source_key: str, dest_key: str = None) -> str:
    if not is_configured():
        return source_key
    if dest_key is None:
        dest_key = source_key
    get_client().copy_object(
        CopySource={"Bucket": R2_PRIVATE_BUCKET, "Key": source_key},
        Bucket=R2_PUBLIC_BUCKET,
        Key=dest_key,
    )
    return dest_key


def get_public_url(key: str) -> str:
    if not is_configured():
        return ""
    if R2_PUBLIC_URL:
        return f"{R2_PUBLIC_URL.rstrip('/')}/{key}"
    return get_presigned_download_url(key, bucket=R2_PUBLIC_BUCKET, expires_in=86400 * 365)


def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()
