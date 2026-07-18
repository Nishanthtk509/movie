import uuid
import logging

import boto3
from django.conf import settings

logger = logging.getLogger(__name__)


def get_b2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.B2_ENDPOINT_URL,
        aws_access_key_id=settings.B2_KEY_ID,
        aws_secret_access_key=settings.B2_APPLICATION_KEY,
    )


def generate_presigned_upload_url(filename, content_type, expires_in=3600):
    """
    Returns (upload_url, key) for a direct-to-B2 PUT upload.
    """

    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    key = f"movies/{uuid.uuid4().hex}.{ext}"

    # Normalize content type
    if not content_type:
        content_type = "application/octet-stream"

    if content_type == "video/matroska":
        content_type = "video/x-matroska"

    client = get_b2_client()

    upload_url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.B2_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
        HttpMethod="PUT",
    )

    return upload_url, key


def delete_b2_object(key):
    if not key:
        return

    client = get_b2_client()

    try:
        client.delete_object(
            Bucket=settings.B2_BUCKET_NAME,
            Key=key,
        )
    except Exception:
        logger.exception("Failed to delete B2 object: %s", key)
        raise