# from faker import Faker
# import qrcode
#
# from core.models import QRCode
#
# fake = Faker()
#
#
# def qr_creator():
#     for i in range(5):
#         QRCode.objects.create(hash="Hash", password="Password")
#         # name = fake.word().capitalize()
#         img = qrcode.make(f"{i}")
#         img.save(f"static/qr_codes/{i}.png")
#     return HttpResponse("")
#
#
# qr_creator()
