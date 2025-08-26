from unfazed.contrib.common.schema import ErrorResponse
from unfazed.http import JsonResponse
from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class CommonMiddleware(BaseMiddleware):
    """
    Contrib CommonMiddleware used for contrib/admin and contrib/auth.

    if you use above two apps

    set `unfazed.contrib.common.middleware.CommonMiddleware` in your entry/routes.py or settings.py

    Usage:

    1、set `unfazed.contrib.common.middleware.CommonMiddleware` in your entry/routes.py or settings.py
    ```python

    from unfazed.route import path, include


    patterns = [
        path("/api/admin/", include("unfazed.contrib.admin"), middlewares=["unfazed.contrib.common.middleware.CommonMiddleware"]),
        path("/api/auth/", include("unfazed.contrib.auth"), middlewares=["unfazed.contrib.common.middleware.CommonMiddleware"]),
    ]

    ```

    2、set `unfazed.contrib.common.middleware.CommonMiddleware` in your settings.py

    ```python

    MIDDLEWARES = [
        "unfazed.contrib.common.middleware.CommonMiddleware",
    ]

    ```

    """

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as err:
            if hasattr(err, "code"):
                code = err.code
            else:
                code = 500

            if hasattr(err, "message"):
                message = err.message
            else:
                message = str(err)

            response = JsonResponse(ErrorResponse(code=code, message=message))
            await response(scope, receive, send)
