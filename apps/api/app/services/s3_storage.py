import boto3
from botocore.config import Config
from typing import Tuple, Dict, Any, Optional
from app.core.config import settings
from app.core.security import compute_sha256

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg"
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def get_s3_client():
    """Returns configured boto3 S3 client with standard regional signature."""
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )

def validate_and_upload_to_s3(
    file_bytes: bytes,
    object_key: str,
    content_type: str,
    metadata: Optional[Dict[str, str]] = None
) -> Tuple[str, str, str]:
    """
    Validates file MIME type, enforces 10MB size limit, computes SHA-256,
    and uploads to private AWS S3 bucket with Server-Side Encryption (AES256).
    Returns (s3_bucket, s3_key, sha256_hash).
    """
    # 1. Size Validation
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size {len(file_bytes)} bytes exceeds maximum 10MB limit.")

    # 2. Type Validation
    normalized_type = content_type.lower()
    if normalized_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"MIME type '{content_type}' is not allowed. Supported: {list(ALLOWED_MIME_TYPES.keys())}")

    # 3. Compute SHA-256
    sha256_hash = compute_sha256(file_bytes)

    # 4. Upload to S3 with ServerSideEncryption
    s3 = get_s3_client()
    upload_meta = metadata or {}
    upload_meta["sha256_hash"] = sha256_hash

    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=object_key,
        Body=file_bytes,
        ContentType=normalized_type,
        ServerSideEncryption="AES256",
        Metadata=upload_meta
    )

    return settings.S3_BUCKET, object_key, sha256_hash

def generate_presigned_download_url(object_key: str, expiration_seconds: int = 300) -> str:
    """
    Generates a secure, temporary pre-signed S3 download URL valid for 5 minutes (300 seconds).
    Only authorized callers (admin or document owner) can trigger this generation.
    """
    s3 = get_s3_client()
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": object_key},
        ExpiresIn=expiration_seconds
    )
    return url

def check_s3_file_integrity(object_key: str, expected_sha256: str) -> bool:
    """
    Downloads file bytes from S3 and verifies that current hash matches the expected SHA-256.
    """
    s3 = get_s3_client()
    try:
        response = s3.get_object(Bucket=settings.S3_BUCKET, Key=object_key)
        content = response["Body"].read()
        return compute_sha256(content) == expected_sha256
    except Exception:
        return False
