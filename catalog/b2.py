from django.http import JsonResponse
from django.conf import settings
import boto3

def test_b2(request):
    try:
        client = boto3.client(
            "s3",
            endpoint_url=settings.B2_ENDPOINT_URL,
            aws_access_key_id=settings.B2_KEY_ID,
            aws_secret_access_key=settings.B2_APPLICATION_KEY,
        )

        buckets = client.list_buckets()

        return JsonResponse({
            "success": True,
            "buckets": buckets["Buckets"],
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
        })