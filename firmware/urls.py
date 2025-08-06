from django.urls import path
from .views import check_firmware

urlpatterns = [
    path('check-firmware/', check_firmware, name='check-firmware'),
]
