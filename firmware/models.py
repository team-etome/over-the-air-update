from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

# Force S3 storage for firmware files
s3_storage = S3Boto3Storage()

class Firmware(models.Model):
    
    version            = models.CharField(max_length=50)
    description        = models.TextField()
    file               = models.FileField(storage=s3_storage, upload_to='firmware/') 
    file_size          = models.BigIntegerField(blank=True, null=True)
    is_latest          = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now_add=True)
    device_version     = models.CharField(blank=True , null=True)

    def save(self, *args, **kwargs):
        if self.is_latest:
            # Unmark other firmware versions
            Firmware.objects.update(is_latest=False)
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.version}"
