from asgiref.typing import (
    ASGIApplication,
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPScope,
)
from starlette.types import Message

from unfazed.conf import settings
from unfazed.contrib.session.settings import SessionSettings
from unfazed.utils import import_string


class SessionMiddleware:
    def __init__(self, app: ASGIApplication):
        self.app = app

        self.setting: SessionSettings = settings["SESSION_SETTINGS"]
        self.engine_cls = import_string(self.setting.engine)

    async def __call__(
        self, scope: HTTPScope, receive: ASGISendCallable, send: ASGIReceiveCallable
    ):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # connection = HTTPConnection(scope)
        session_store = self.engine_cls(self.setting.cookie_name)
        scope["session"] = session_store

        async def wrapped_send(message: Message):
            pass
