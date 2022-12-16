from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from core.models import QRCode


class QRPasswordForm(ModelForm):
    class Meta:
        model = QRCode
        fields = ["password"]


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["phone"]

    def clean(self):
        cleaned_data = super().clean()
        try:
            if bool(cleaned_data["phone"]):
                if get_user_model().objects.filter(phone=cleaned_data["phone"]).exists():
                    raise ValidationError("User with this phone number already exists.")

            elif not bool(cleaned_data["phone"]):
                raise ValidationError("Write down your phone number to proceed registration please.")

        except KeyError:
            raise ValidationError("Enter a valid info please")

        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """

    username = UsernameField(label="Phone", widget=forms.TextInput(attrs={"autofocus": True}))
