import logging
from typing import Any

import httpx
from django.conf import settings
from django.contrib.auth.backends import BaseBackend

from .models import AdminUser

logger = logging.getLogger(__name__)


class ExternalUserAuthBackend(BaseBackend):
    """Авторизация сотрудника через внутренний сервис."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_data = self._login(username, password)
        if not login_data:
            return None

        try:
            user = AdminUser.objects.get(external_id=login_data["employer_id"])
        except AdminUser.DoesNotExist:
            return None

        if request is not None and hasattr(request, "session"):
            tokens = login_data.get("tokens", {})
            request.session["access_token"] = tokens.get("access_token")
            request.session["refresh_token"] = tokens.get("refresh_token")
            request.session.save()

        return user

    @staticmethod
    def _login(
        username: str | None = None,
        password: str | None = None,
    ) -> dict[str, Any] | None:
        if not username or not password:
            return None

        try:
            timeout = httpx.Timeout(10.0, read=10.0)
            with httpx.Client(timeout=timeout) as httpx_client:
                response = httpx_client.post(
                    url=settings.INNER_AUTH_URLS["authenticate"],
                    json={
                        "email": username,
                        "password": password,
                    },
                )

                if response.status_code != 200:
                    return None

                return response.json()

        except (
            httpx.TimeoutException,
            httpx.RequestError,
            httpx.HTTPStatusError,
        ) as ex:
            logger.error(f"Error login user: {ex}")

    def get_user(self, user_id) -> AdminUser | None:
        try:
            return AdminUser.objects.get(pk=user_id)

        except AdminUser.DoesNotExist:
            return None
