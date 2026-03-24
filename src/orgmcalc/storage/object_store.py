"""Object storage client for R2/S3-compatible storage."""

from __future__ import annotations

from typing import Any

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from orgmcalc.config import get_settings

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
ALLOWED_PDF_TYPE = "application/pdf"
ALLOWED_CONTENT_TYPES = ALLOWED_IMAGE_TYPES | {ALLOWED_PDF_TYPE}

CONTENT_TYPE_TO_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
    "application/pdf": "pdf",
}


def extension_from_content_type(content_type: str) -> str:
    ct = (content_type or "").split(";")[0].strip().lower()
    return CONTENT_TYPE_TO_EXT.get(ct, "bin")


class ObjectStore:
    """Client for R2/S3-compatible object storage."""

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint_url = settings.r2_endpoint_url
        self._access_key = settings.r2_access_key_id
        self._secret_key = settings.r2_secret_access_key
        self._bucket = settings.r2_bucket_name
        self._client: Any = None

        if self._endpoint_url and self._access_key and self._secret_key and self._bucket:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name="auto",
                config=Config(signature_version="s3v4"),
            )

    @property
    def available(self) -> bool:
        return self._client is not None

    def upload_bytes(self, key: str, content: bytes, content_type: str) -> str | None:
        if not self._client:
            return None
        try:
            self._client.put_object(
                Bucket=self._bucket, Key=key, Body=content, ContentType=content_type
            )
            return self.get_presigned_url(key)
        except ClientError:
            return None

    def get_presigned_url(self, key: str, expiration: int = 3600) -> str | None:
        if not self._client:
            return None
        try:
            result: str = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expiration,
            )
            return result
        except ClientError:
            return None


_store: ObjectStore | None = None


def get_object_store() -> ObjectStore:
    global _store
    if _store is None:
        _store = ObjectStore()
    return _store
