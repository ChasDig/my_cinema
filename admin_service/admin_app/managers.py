import logging

import httpx
from django.contrib.auth.models import BaseUserManager

from admin_service.settings import INNER_AUTH_URLS

logger = logging.getLogger(__name__)


class ExternalUserManager(BaseUserManager):
    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        **extra_fields,
    ):
        with httpx.Client(timeout=10) as httpx_client:
            response = httpx_client.post(
                url=INNER_AUTH_URLS["create_user"],
                json={
                    "username": username,
                    "password": password,
                    "email": email,
                    "is_staff": extra_fields.get("is_staff", False),
                    "is_superuser": extra_fields.get("is_superuser", False),
                },
            )

            if response.status_code != 201:
                raise ValueError(f"Error create AdminUser: {response.json()}")

            try:
                external_id = response.json()["employer_id"]

            except KeyError:
                raise ValueError("Error create AdminUser")

        user = self.model(
            external_id=external_id,
            username=username,
            email=email,
            **extra_fields,
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(
            username=username, password=password, email=email, **extra_fields
        )
