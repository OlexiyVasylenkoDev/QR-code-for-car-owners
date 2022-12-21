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
        self.request.session["qr"] = self.kwargs["hash"]
        print(self.request.session.items())
        qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])
        if qr_code.password == form.data["password"]:
            if self.request.user.is_authenticated:
                qr_code.is_active = True
                qr_code.user = self.request.user
                qr_code.save()
            return super().form_valid(form)
        else:
            """Add message for wrong password"""
            return super().form_invalid(form)


class QRCodeTemplateView(TemplateView):
    model = QRCode
    template_name = "qr/qr.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"qr": QRCode.objects.get(hash=kwargs["hash"])}
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
        return self.render_to_response(self.extra_context)


class Registration(CreateView):
    form_class = RegistrationForm
    template_name = "registration/user_form.html"
    success_url = reverse_lazy("core:profile")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("core:profile"))
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        print(self.request.session.items())
        self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        print(self.request.session.items())

        self.object = form.save(commit=True)
        self.object.is_active = True
        self.object.save()

        login(self.request, self.object)

        if "qr" in self.request.session.keys():
            qr = QRCode.objects.get(hash=self.request.session["qr"])
            qr.is_active = True
            qr.user = self.request.user
            qr.save()
            self.request.session.pop("qr")

        return HttpResponseRedirect(self.success_url)


class Login(LoginView):
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        print(self.request.session.items())
        login(self.request, form.get_user())

        if "qr" in self.request.session.keys():
            qr = QRCode.objects.get(hash=self.request.session["qr"])
            qr.is_active = True
            qr.user = self.request.user
            qr.save()
            self.request.session.pop("qr")
        print(self.request.session.items())
        return HttpResponseRedirect(self.get_success_url())


class Logout(LogoutView):
    next_page = reverse_lazy("core:index")


@user_passes_test(lambda user: user.is_superuser)
def generate_qr(request):
    for i in range(1):
        hash_uuid = uuid.uuid4
        hash = Hasher.encode(self=Hasher(), password=hash_uuid, salt=Hasher.salt(self=Hasher())).replace("/", "_")[21:]
        QRCode.objects.create(hash=hash, password=fake.password(length=10))
        data = f"http://127.0.0.1:3456/{hash}"
        img = make(data)
        img_name = f"{hash}.png"
        img.save(str(settings.STATIC_ROOT) + '/qr_codes/' + img_name)
    return HttpResponse("QR-codes generated!")
