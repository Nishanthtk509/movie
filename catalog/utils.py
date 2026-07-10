import boto3
from django.conf import settings

def get_b2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.B2_ENDPOINT_URL,
        aws_access_key_id=settings.B2_KEY_ID,
        aws_secret_access_key=settings.B2_APPLICATION_KEY,
        region_name=settings.B2_REGION,
    )

def delete_b2_object(key):
    """Delete a video from B2. Safe to call even if key is empty/None."""
    if not key:
        return
    s3 = get_b2_client()
    s3.delete_object(Bucket=settings.B2_BUCKET_NAME, Key=key)


    