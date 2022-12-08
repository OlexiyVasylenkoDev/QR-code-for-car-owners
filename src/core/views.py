from django.http import HttpResponse
from django.shortcuts import render
from faker import Faker
import qrcode

from core.models import QRCode

fake = Faker()


# Create your views here.
def qr_creator(request):
    for i in range(5):
        hash = fake.word()
        QRCode.objects.create(hash=hash, password="Password")
        # name = fake.word().capitalize()
        img = qrcode.make(f"{hash}")
        img.save(f"{hash}.png")
    return HttpResponse("Done!")
