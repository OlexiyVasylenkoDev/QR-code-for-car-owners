from django.urls import path

from core.views import (
    Index,
    Login,
    Logout,
    Profile,
    QRCodeView,
    Registration,
    UpdateProfile,
    UpdateQRCode,
    VerificationView,
    generate_qr,
    multithreading,
    send_verification_sms,
)

app_name = "core"

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("registration/", Registration.as_view(), name="registration"),
    path("profile/", Profile.as_view(), name="profile"),
    path("profile/update/<str:pk>", UpdateProfile.as_view(), name="update_profile"),
    # path("generate_qr/", generate_qr, name="generate_qr"),
    path("multithreading/", multithreading, name="multithreading"),
    path("qr/<str:hash>/", QRCodeView.as_view(), name="qr_code_view"),
    path("qr/update/<str:pk>/", UpdateQRCode.as_view(), name="update_qr_code"),
    path("send_verification_sms/", send_verification_sms, name="send_verification_sms"),
    path("verification/", VerificationView.as_view(), name="verification"),
]
