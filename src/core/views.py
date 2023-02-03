import multiprocessing
import threading
import time
import uuid
from multiprocessing.pool import ThreadPool

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from qrcode import make

from core.forms import CustomAuthenticationForm, RegistrationForm, VerificationForm
from core.models import QRCode
from core.utils.hasher import Hasher
from core.utils.qr_code_assigner import QRCodeAssigner
from core.utils.verify_qr_code import Verifier


class Index(TemplateView):
    template_name = "index/index.html"

    def get(self, request, *args, **kwargs):
        self.extra_context = {"qr_code": QRCode.objects.last()}
        return self.render_to_response(self.extra_context)


class VerificationView(FormView, Verifier):
    form_class = VerificationForm
    template_name = "index/verification.html"
    success_url = reverse_lazy("core:login")

    def get(self, request, *args, **kwargs):
        if "redirect_to_verification" in request.session:
            return super().get(self, request, *args, **kwargs)
        else:
            raise Http404

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context.update({"my_message": "Something went wrong"})
        return self.render_to_response(context)

    def form_valid(self, form):
        # if "redirect_to_verification" in self.request.session:
        if self.request.user.is_authenticated:
            qr_code = QRCode.objects.get(hash__exact=self.kwargs["hash"])
            if self.request.session.get("verification_code") == form.data["code"]:
                qr_code.is_active = True
                qr_code.user = self.request.user
                qr_code.save()
                return super().form_valid(form)
            else:
                # raise ValidationError("User with this phone number already exists.")
                # """Add message for wrong password"""
                return super().form_invalid(form)
        else:
            if self.request.session.get("verification_code") == form.data["code"]:
                registered_user = get_user_model().objects.get(
                    phone=self.request.session.get("user")
                )
                registered_user.is_active = True
                registered_user.save()

                login(self.request, registered_user)

                # return self.assign_qr()
                return super().form_valid(form)
            else:
                # raise ValidationError("User with this phone number already exists.")
                # """Add message for wrong password"""
                return super().form_invalid(form)

    # else:
    #     raise 404


class TemplateView(TemplateView):
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
        view = TemplateView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._add_hash_to_session()
        self.request.session["redirect_to_verification"] = True
        view = VerificationView.as_view()
        if self.request.user.is_authenticated:
            return view(request, *args, **kwargs)
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
    template_name = "user/user_profile.html"

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
    template_name = "user/user_update.html"
    success_url = reverse_lazy("core:profile")


class Login(LoginView, QRCodeAssigner):
    authentication_form = CustomAuthenticationForm
    template_name = "user/user_login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        login(self.request, form.get_user())
        return self.assign_qr()

        # print(self.request.session.items())
        # return HttpResponseRedirect(self.get_success_url())


class Registration(CreateView, QRCodeAssigner):
    form_class = RegistrationForm
    template_name = "user/user_registration.html"
    success_url = reverse_lazy("core:profile")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("core:profile"))
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.request.session["redirect_to_verification"] = True
        if "qr" not in self.request.session.keys():
            self.object = form.save(commit=False)
            self.object.is_active = False
            self.object.save()
            self.request.session["user"] = str(self.object)
            return HttpResponseRedirect(reverse_lazy("core:verification"))
        self.object = form.save(commit=True)
        self.object.is_active = True
        self.object.save()
        login(self.request, self.object)
        return self.assign_qr()


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
        img.save(str(settings.STATIC_ROOT) + "/qr_codes/" + img_name)
    final_time = time.time()
    print(f"Estimated time: {final_time - start_time} seconds.")
    return HttpResponse("QR-codes generated!")


workers = 10
DATA_SIZE = 5


@user_passes_test(lambda user: user.is_superuser)
def multithreading(request):
    with ThreadPool(workers) as pool:
        input_data = [DATA_SIZE // workers for _ in range(workers)]
        pool.map(generate_qr, input_data)
    return HttpResponse("QR-codes generated with multithreading!")


def send_verification_sms(request):
    if "redirect_to_verification" in request.session:
        if request.session.get("qr"):
            Verifier(request).send_verification_code(request.user)
        else:
            Verifier(request).send_verification_code(request.session.get("user"))
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    else:
        raise Http404
