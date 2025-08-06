from django.contrib import admin
from .models import Firmware

@admin.register(Firmware)
class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_latest', 'file_size', 'created_at')
    readonly_fields = ('file_size', 'created_at')
    list_editable = ('is_latest',)
