from core.models import QRCode


class QRCodeAssigner:
    def assign_qr(self):
        if "qr" in self.request.session.keys():
            qr = QRCode.objects.get(hash=self.request.session["qr"])
            qr.is_active = True
            qr.user = self.request.user
            qr.save()
            self.request.session.pop("qr")
