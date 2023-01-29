from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model

from core.models import QRCode

admin.site.register([get_user_model(), QRCode])
