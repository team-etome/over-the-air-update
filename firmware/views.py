from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Firmware
import boto3

# views.py
import boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from packaging import version  # pip install packaging

from .models import Firmware


class CheckFirmwareView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        device_version  = request.query_params.get('device_version')
        current_version = request.query_params.get('current_version')

        if not device_version:
            return Response(
                {"detail": "device_version is required as a query param"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only consider firmware for this specific device_version
        qs = Firmware.objects.filter(device_version=device_version)

        if not qs.exists():
            return Response({
                "update_available": False,
                "device_version": device_version,
                "latest_version": None,
                "message": "No firmware found for this device_version."
            }, status=status.HTTP_200_OK)

        # Prefer is_latest=True; otherwise, newest by created_at
        fw = qs.filter(is_latest=True).first() or qs.order_by('-created_at').first()

        # If client supplied current_version, compare semantically
        if current_version:
            try:
                if version.parse(current_version) >= version.parse(fw.version):
                    # Already up-to-date for this device_version
                    return Response({
                        "update_available": False,
                        "device_version": device_version,
                        "latest_version": fw.version,
                        "release_notes": fw.description,
                        "file_size": fw.file_size,
                    }, status=status.HTTP_200_OK)
            except Exception:
                # If parsing fails, treat as update available
                pass

        # If we reach here, an update is available (or current_version not provided)
        return Response({
            "update_available": True,
            "device_version": device_version,
            "latest_version": fw.version,
            "release_notes": fw.description,
            "file_size": fw.file_size,
            "download_url": self._presigned_url(fw),
        }, status=status.HTTP_200_OK)

    def _presigned_url(self, fw):
        """Generate short-lived S3 pre-signed URL for the firmware file."""
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', None)
        )
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': fw.file.name},
            ExpiresIn=1200  # 20 minutes
        )
