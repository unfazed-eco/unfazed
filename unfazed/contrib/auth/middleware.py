from functools import cache

from asgiref.typing import (
    ASGIApplication,
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPScope,
)

from unfazed.conf import settings
from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.settings import UnfazedContribAuthSettings
from unfazed.utils import import_string


@cache
def get_anonymous_user(function_str: str | None = None) -> AbstractUser | None:
    if function_str is None:
        return None
    func = import_string(function_str)

    return func()


class AuthenticationMiddleware:
    def __init__(self, app: ASGIApplication):
        self.app = app

        self.setting: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]

        self.anonymous_user = get_anonymous_user(self.setting.ANONYMOUS_USER_INSTANCE)

    async def __call__(
        self, scope: HTTPScope, receive: ASGISendCallable, send: ASGIReceiveCallable
    ):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        if "user" in scope:
            await self.app(scope, receive, send)
            return

        session = scope.get("session")
        if session is None:
            user = self.anonymous_user

        else:
            UserCls = AbstractUser.UserCls()
            user_id = session.get("id")
            user = await UserCls.get(id=user_id)

        scope["user"] = user

        await self.app(scope, receive, send)
