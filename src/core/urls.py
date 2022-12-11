from django.urls import path

from core.views import generate_qr, Login, Registration, Index, CheckQRPassword

app_name = "core"

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('generate_qr/', generate_qr, name="generate_qr"),
    # path('qr/<str:hash>/', QRCodeView.as_view(), name="hash_view"),
    path('qr/check/<str:hash>/', CheckQRPassword.as_view(), name="check_qr_password"),
    path('login/', Login.as_view(), name="login"),
    path('registration/', Registration.as_view(), name="registration"),
]
