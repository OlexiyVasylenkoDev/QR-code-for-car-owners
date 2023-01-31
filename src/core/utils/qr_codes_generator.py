import uuid

import qrcode
from django.conf import settings
from PIL import Image
from qrcode import make

from core.models import QRCode
from core.utils.hasher import Hasher
from core.views import fake


def generate_qr():
    for i in range(1):
        hash_uuid = uuid.uuid4
        hash = Hasher.encode(
            self=Hasher(), password=hash_uuid, salt=Hasher.salt(self=Hasher())
        ).replace("/", "_")[21:]
        QRCode.objects.create(hash=hash, password=fake.password(length=10))
        print(i)
        data = f"https://{settings.ALLOWED_HOSTS[0]}/qr/{hash}"
        img = make(data)
        img_name = f"{hash}.png"
        img.save(
            str("AAAAAAAAAAA" + settings.STATICFILES_DIRS[0]) + "/qr_codes/" + img_name
        )
    return "Success!"


def qr_with_picture():
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


generate_qr()
