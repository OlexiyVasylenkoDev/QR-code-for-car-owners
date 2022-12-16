import pprint
import uuid

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, FormView
from multi_form_view import MultiModelFormView
from qrcode import make

from core.forms import RegistrationForm, CustomAuthenticationForm, QRPasswordForm
from core.models import QRCode

# Create your views here.
from faker import Faker
from core.utils.hasher import Hasher

fake = Faker()


class Index(TemplateView):
    template_name = "index/index.html"


class QRCodeActivationView(FormView):
    model = QRCode
    form_class = QRPasswordForm
    template_name = "qr/check_qr.html"
    success_url = reverse_lazy("core:login")

    def form_valid(self, form):
        qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])
        if qr_code.password == form.data["password"]:
            if self.request.user:
                qr_code.is_active = True
                qr_code.user = self.request.user
                qr_code.save()
                self.success_url = reverse_lazy("core:profile")
            return super().form_valid(form)
        else:
            return HttpResponse("Oops! Something went wrong")


class QRCodeTemplateView(TemplateView):
    model = QRCode
    template_name = "qr/qr.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"qr": QRCode.objects.get(hash=kwargs["hash"])}
        print(self.extra_context)
        return self.render_to_response(self.extra_context)


class QRCodeView(View):

    def get(self, request, *args, **kwargs):
        view = QRCodeTemplateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = QRCodeActivationView.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if QRCode.objects.get(hash=self.kwargs["hash"]).is_active:
            return self.get(request, *args, **kwargs)
        return self.post(request, *args, **kwargs)


class Profile(LoginRequiredMixin, TemplateView):
    template_name = "registration/profile.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"user": self.request.user,
                              "qr_codes": QRCode.objects.filter(user=self.request.user) or None}
        print(self.extra_context)
        return self.render_to_response(self.extra_context)


class Registration(CreateView):
    form_class = RegistrationForm
    template_name = "registration/user_form.html"
    success_url = reverse_lazy("core:profile")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("core:profile"))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=True)
        self.object.is_active = True
        self.object.save()
        login(self.request, self.object, backend="core.auth_backend.AuthBackend")
        return HttpResponseRedirect(self.success_url)


class Login(LoginView):
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True


class Logout(LogoutView):
    next_page = reverse_lazy("core:index")


@user_passes_test(lambda user: user.is_superuser)
def generate_qr(request):
    for i in range(5):
        hash_uuid = uuid.uuid4
        hash = Hasher.encode(self=Hasher(), password=hash_uuid, salt=Hasher.salt(self=Hasher())).replace("/", "_")
        QRCode.objects.create(hash=hash, password=fake.password(length=10))
        data = f"http://127.0.0.1:3456/view/{hash}"
        img = make(data)
        img_name = f"{hash[21:40]}.png"
        img.save(str(settings.STATICFILES_DIRS[0]) + '/qr_codes/' + img_name)
    return HttpResponse("QR-codes generated!")


class SchoolDataLogin(MultiModelFormView):
    form_classes = {
        'qr_form': QRPasswordForm,
        'user_form': CustomAuthenticationForm,
    }
    template_name = 'home_login.html'

    def post(self, request, *args, **kwargs):
        self.extra_context = {"hash": self.kwargs["hash"]}
        return self.render_to_response(self.extra_context)

    def forms_valid(self, forms):
        print(self.kwargs)
        qr = forms['qr_form']
        user = forms['user_form'].save(commit=True)

        qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])

        user.is_active = True
        user.save()

        login(self.request, user, backend="core.auth_backend.AuthBackend")

        if qr_code.password == qr.data["password"]:
            qr_code.is_active = True
            qr_code.user = self.request.user
            qr_code.save()
            self.success_url = reverse_lazy("core:index")
            return HttpResponseRedirect(reverse_lazy("core:index"))
        else:
            return HttpResponse("Oops! Something went wrong")


class SchoolDataRegistration(MultiModelFormView):
    form_classes = {
        'qr_form': QRPasswordForm,
        'user_form': RegistrationForm,
    }
    template_name = 'home_registration.html'

    def post(self, request, **kwargs):
        self.extra_context = {"hash": self.kwargs["hash"]}
        return self.render_to_response(self.extra_context)

    def forms_valid(self, forms):
        qr = forms['qr_form']
        user = forms['user_form'].save(commit=True)

        qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])

        user.is_active = True
        user.save()

        login(self.request, user, backend="core.auth_backend.AuthBackend")

        if qr_code.password == qr.data["password"]:
            qr_code.is_active = True
            qr_code.user = self.request.user
            qr_code.save()
            self.success_url = reverse_lazy("core:index")
            return HttpResponseRedirect(reverse_lazy("core:index"))
        else:
            return HttpResponse("Oops! Something went wrong")
