from django.urls import path

from core.views import generate_qr, Login, Logout, Registration, QRCodeView, Profile, Index, \
    SchoolDataRegistration, SchoolDataLogin

app_name = "core"

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('login/', Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path('registration/', Registration.as_view(), name="registration"),
    path('profile/', Profile.as_view(), name="profile"),
    path('generate_qr/', generate_qr, name="generate_qr"),

    path('view/<str:hash>/login/', SchoolDataLogin.as_view(), name="view_login"),
    path('view/<str:hash>/register/', SchoolDataRegistration.as_view(), name="view_register"),

    path('qr/<str:hash>/', QRCodeView.as_view(), name="qr_code_view"),
]
