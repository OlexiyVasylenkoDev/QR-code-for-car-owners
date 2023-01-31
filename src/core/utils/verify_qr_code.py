import os
import random

from twilio.rest import Client

from core.models import QRCode


class QRCodeVerifier:
    def __init__(self, phone_number, code):
        self.request = None
        self.code = None

    ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
    AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
    CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)

    # list_of_nums = [i for i in range(10)]
    # code = ''.join([str(i) for i in random.choices(list_of_nums, k=8)])

    def verify_qr(self, phone_number):
        list_of_nums = [i for i in range(10)]
        code = ''.join([str(i) for i in random.choices(list_of_nums, k=8)])
        # message = self.CLIENT.messages.create(
        #     body=f'Your verification code is: {code}',
        #     from_=os.environ['TWILIO_PHONE_NUMBER'],
        #     to=phone_number
        # )
        # print(message.sid)
        # self.code = code
        print(self.code)
        print(f"SMS to: {phone_number}\nText: {self.code}")

    # def verify_qr(self):
    #     if QRCode.objects.filter(hash=self.request.path.split("/")[2]).exists():
    #         print(QRCode.objects.get(hash=self.request.path.split("/")[2]).password)
