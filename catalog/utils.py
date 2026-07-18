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
    The key is randomized so uploaded filenames never collide or leak
    the original filename.
    """
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    key = f"movies/{uuid.uuid4().hex}.{ext}"

    client = get_b2_client()
    upload_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.B2_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )
    return upload_url, key


def delete_b2_object(key):
    """
    Deletes an object from B2 by key. Safe to call with an empty/None key
    (no-op) so callers don't need to guard every call site.
    """
    if not key:
        return

    client = get_b2_client()
    try:
        client.delete_object(Bucket=settings.B2_BUCKET_NAME, Key=key)
    except Exception:
        logger.exception("Failed to delete B2 object with key %s", key)
        raise