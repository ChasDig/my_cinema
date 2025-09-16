import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware: добавление времени выполнение запроса."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start_t = time.perf_counter()
        response: Response = await call_next(request)

        response.headers["X-Process-Time"] = str(time.perf_counter() - start_t)
        return response
