from rest_framework import serializers
from .models import Firmware

class FirmwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firmware
        fields = ['version', 'description', 'file_size']
