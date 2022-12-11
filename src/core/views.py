import pprint
import time
import uuid

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, FormView
from qrcode import make

from core.forms import RegistrationForm, CustomAuthenticationForm, QRPasswordForm
from core.models import QRCode

# Create your views here.
from faker import Faker
from core.utils.hasher import Hasher

fake = Faker()


class Index(TemplateView):
    template_name = "index/index.html"


# class QRCodeView(TemplateView):
#     model = QRCode
#     template_name = "qr/check_qr.html"
#     next_page = reverse_lazy("core:check_qr_password")
#
#     def get(self, request, *args, **kwargs):
#         self.extra_context = {"qr": QRCode.objects.get(hash=kwargs["hash"]),
#                               "photo": "qr_codes/" + kwargs["hash"][21:40] + ".png"}
#         pprint.pprint(request.META["PATH_INFO"].replace("/qr/", "")[:-1])
#         return HttpResponseRedirect(reverse_lazy("core:check_qr_password"))

#    def check_password(self):
#        print(self.extra_context["qr"].password)


class CheckQRPassword(FormView):
    model = QRCode
    form_class = QRPasswordForm
    template_name = "qr/check_qr.html"
    success_url = reverse_lazy("core:login")

    def form_valid(self, form):
        if QRCode.objects.get(hash__exact=self.kwargs["hash"]).password == form.data["password"]:
            return super().form_valid(form)
        else:
            return HttpResponse("Oops! Something went wrong")


class Login(LoginView):
    authentication_form = CustomAuthenticationForm
    next_page = reverse_lazy("core:index")


class Registration(CreateView):
    form_class = RegistrationForm
    template_name = "registration/user_form.html"
    success_url = reverse_lazy("core:index")

    def form_valid(self, form):
        print(self.kwargs)
        self.object = form.save(commit=True)
        self.object.is_active = True
        self.object.save()

        login(self.request, self.object, backend="core.auth_backend.AuthBackend")
        return HttpResponseRedirect(self.success_url)


# def registration(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             verify.send(form.cleaned_data.get('phone'))
#             return redirect('index')
#     else:
#         form = RegistrationForm()
#     return render(request, 'registration/user_form.html', {'form': form})


@user_passes_test(lambda user: user.is_superuser)
def generate_qr(request):
    for i in range(10000):
        hash_uuid = uuid.uuid4
        hash = Hasher.encode(self=Hasher(), password=hash_uuid, salt=Hasher.salt(self=Hasher())).replace("/", "_")
        QRCode.objects.create(hash=hash, password=fake.password())
        data = f"http://127.0.0.1:3456/{hash}"
        img = make(data)
        img_name = f"{hash[21:40]}.png"
        img.save(str(settings.STATICFILES_DIRS[0]) + '/qr_codes/' + img_name)
    return HttpResponse("QR-codes generated!")
