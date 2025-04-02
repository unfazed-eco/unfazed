import typing as t

from unfazed.conf import settings
from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.settings import UnfazedContribAuthSettings
from unfazed.type import ASGIApp, Receive, Scope, Send

if t.TYPE_CHECKING:
    from unfazed.contrib.session.backends.base import SessionBase  # pragma: no cover


class AuthenticationMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

        self.setting: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        if "user" in scope:
            await self.app(scope, receive, send)
            return

        session: "SessionBase" = t.cast("SessionBase", scope.get("session"))
        if session is None or (self.setting.SESSION_KEY not in session):
            user = None

        else:
            session_dict = session[self.setting.SESSION_KEY]
            UserCls = AbstractUser.UserCls()
            user = await UserCls.from_session(session_dict)

        scope["user"] = user

        await self.app(scope, receive, send)
