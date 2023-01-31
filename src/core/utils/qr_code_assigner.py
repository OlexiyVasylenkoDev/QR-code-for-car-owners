from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from core.models import QRCode


class QRCodeAssigner:
    def assign_qr(self):
        if "qr" in self.request.session.keys():
            return HttpResponseRedirect(reverse_lazy("core:qr_code_view", kwargs={
                "hash": self.request.session.get("qr")
            }))
        return HttpResponseRedirect(self.get_success_url())
            # qr = QRCode.objects.get(hash=self.request.session["qr"])
            # qr.is_active = True
            # qr.user = self.request.user
            # qr.save()
            # self.request.session.pop("qr")
