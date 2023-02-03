import os
import random

from twilio.rest import Client


class Verifier:
    def __init__(self, request):
        self.request = request

    ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
    AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
    CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)

    def send_verification_code(self, phone_number):
        list_of_nums = [i for i in range(10)]
        code = "".join([str(i) for i in random.choices(list_of_nums, k=8)])
        self.request.session["verification_code"] = code
        message = self.CLIENT.messages.create(
            body=f'Your verification code is: {code}',
            from_=os.environ['TWILIO_PHONE_NUMBER'],
            to=phone_number
        )
