from django.urls import path
from .views import CheckFirmwareView

urlpatterns = [
    path('api/check-firmware/', CheckFirmwareView.as_view(), name='check-firmware'),
]
