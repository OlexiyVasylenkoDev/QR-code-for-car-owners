from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
from core.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        unique=True,
        db_index=True,
        editable=False,
    )
    phone = PhoneNumberField(
        _("phone"),
        unique=True,
        null=True,
        blank=True,
    )
    telegram = models.URLField(
        _("telegram"),
        null=True,
        blank=True,
    )
    whatsapp = models.URLField(
        _("whatsapp"),
        null=True,
        blank=True,
    )
    viber = models.URLField(
        _("viber"),
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )

    USERNAME_FIELD = "phone"

    objects = CustomUserManager()


class QRCode(models.Model):
    hash = models.CharField(max_length=256, primary_key=True, unique=True, null=False, blank=False)
    password = models.CharField(_("password"), max_length=128)
