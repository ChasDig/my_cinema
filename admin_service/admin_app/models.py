from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import ExternalUserManager


class AdminUser(AbstractBaseUser, PermissionsMixin):
    external_id = models.UUIDField()
    username = models.CharField(max_length=128, null=False, unique=True)
    email = models.EmailField(max_length=64, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = ExternalUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]

    def __str__(self):
        return self.username
