import multiprocessing
import threading
import time
import uuid
from multiprocessing.pool import ThreadPool

import qrcode
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from PIL import Image
from qrcode import make

from core.forms import (CustomAuthenticationForm, QRActivationForm,
                        RegistrationForm)
from core.models import QRCode
from core.utils.hasher import Hasher
from core.utils.qr_code_assigner import QRCodeAssigner
from core.utils.verify_qr_code import QRCodeVerifier


class Index(TemplateView):
    template_name = "index/index.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"qr_code": QRCode.objects.last()}
        return self.render_to_response(self.extra_context)


class QRCodeActivationView(FormView, QRCodeVerifier):
    model = QRCode
    form_class = QRActivationForm
    template_name = "qr/qr_activation.html"
    success_url = reverse_lazy("core:login")

    def get(self, request, *args, **kwargs):
        self.verify_qr(self.request.user)
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])
        if self.code == form.data["code"]:
            if self.request.user.is_authenticated:
                qr_code.is_active = True
                qr_code.user = self.request.user
                qr_code.save()
            return super().form_valid(form)
        else:
            """Add message for wrong password"""
            return super().form_invalid(form)


class QRCodeTemplateView(TemplateView, QRCodeVerifier):
    model = QRCode
    template_name = "qr/qr.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"qr": QRCode.objects.get(hash=kwargs["hash"])}
        return self.render_to_response(self.extra_context)


class QRCodeView(View):
    def _add_hash_to_session(self):
        self.request.session["qr"] = self.kwargs["hash"]
        return self.request

    def get(self, request, *args, **kwargs):
        view = QRCodeTemplateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = QRCodeActivationView.as_view()
        if self.request.user.is_authenticated:
            return view(request, *args, **kwargs)
        self._add_hash_to_session()
        return HttpResponseRedirect(reverse_lazy("core:login"))

    def dispatch(self, request, *args, **kwargs):
        if QRCode.objects.get(hash=self.kwargs["hash"]).is_active:
            return self.get(request, *args, **kwargs)
        return self.post(request, *args, **kwargs)


class UpdateQRCode(LoginRequiredMixin, UpdateView):
    model = QRCode
    fields = ["title", "message"]
    template_name = "qr/qr_update.html"
    success_url = reverse_lazy("core:profile")


class Profile(LoginRequiredMixin, TemplateView):
    template_name = "registration/user_profile.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            "user": self.request.user,
            "qr_codes": QRCode.objects.filter(user=self.request.user) or None,
        }
        return self.render_to_response(self.extra_context)


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = [
        "phone",
    ]
    template_name = "registration/user_update.html"
    success_url = reverse_lazy("core:profile")


class Login(LoginView, QRCodeAssigner):
    authentication_form = CustomAuthenticationForm
    template_name = "registration/user_login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        print(self.request.session.items())
        login(self.request, form.get_user())
        return self.assign_qr()

        # print(self.request.session.items())
        # return HttpResponseRedirect(self.get_success_url())


class Registration(CreateView, QRCodeAssigner):
    form_class = RegistrationForm
    template_name = "registration/user_registration.html"
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

        return self.assign_qr()

        # return HttpResponseRedirect(self.success_url)


class Logout(LogoutView):
    next_page = reverse_lazy("core:index")


# @user_passes_test(lambda user: user.is_superuser)
def generate_qr(request):
    start_time = time.time()
    for i in range(DATA_SIZE):
        hash_uuid = uuid.uuid4
        hash = Hasher.encode(
            self=Hasher(), password=hash_uuid, salt=Hasher.salt(self=Hasher())
        ).replace("/", "_")[21:]
        QRCode.objects.create(hash=hash)
        print([threading.current_thread(), multiprocessing.current_process()])
        print(i)
        data = f"https://{settings.ALLOWED_HOSTS[0]}/qr/{hash}"
        img = make(data)
        img_name = f"{hash}.png"
        img.save(str(settings.STATICFILES_DIRS[0]) + "/qr_codes/" + img_name)
    final_time = time.time()
    print(f"Estimated time: {final_time - start_time} seconds.")
    return HttpResponse("QR-codes generated!")


workers = 50
DATA_SIZE = 200


def multithreading(request):
    with ThreadPool(workers) as pool:
        input_data = [DATA_SIZE // workers for _ in range(workers)]
        pool.map(generate_qr, input_data)
    return HttpResponse("QR-codes generated with multithreading!")


def qr_with_picture(request):
    Logo_link = "walkie.png"
    logo = Image.open(str(settings.STATICFILES_DIRS[0]) + "/img/" + Logo_link)
    # taking base width
    basewidth = 100
    # adjust image size
    wpercent = basewidth / float(logo.size[0])
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    # taking url or text
    url = "https://www.geeksforgeeks.org/"
    # adding URL or text to QRcode
    QRcode.add_data(url)
    # generating QR code
    QRcode.make()
    # taking color name from user
    # adding color to QR code
    QRimg = QRcode.make_image(fill_color="black", back_color="white").convert("RGB")
    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    # save the QR code generated
    QRimg.save(str(settings.STATICFILES_DIRS[0]) + "/qr_codes/" + "walkie.png")
    print("QR code generated!")
