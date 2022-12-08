from django.urls import path

from core.views import qr_creator

app_name = "core"

urlpatterns = [
    path('', qr_creator, name="qr_creator"),
]
