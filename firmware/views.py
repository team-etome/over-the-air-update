from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Firmware
import boto3

@api_view(['GET'])
@permission_classes([AllowAny])  # You can later add token authentication
def check_firmware(request):
    current_version = request.query_params.get('current_version')
    firmware = Firmware.objects.filter(is_latest=True).first() or Firmware.objects.latest('created_at')

    # Compare current version with latest
    if current_version == firmware.version:
        return Response({
            "update_available": False,
            "latest_version": firmware.version
        })

    # Generate secure pre-signed URL for download
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME)

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': firmware.file.name},
        ExpiresIn=1200  # URL valid for 10 minutes
    )

    return Response({
        "update_available": True,
        "latest_version": firmware.version,
        "release_notes": firmware.description,
        "file_size": firmware.file_size,
        "download_url": url
    })
