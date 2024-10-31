import typing as t

from asgiref.typing import (
    ASGIApplication,
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPScope,
)
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import Message

from unfazed.conf import settings
from unfazed.contrib.session.backend.base import SessionBase
from unfazed.contrib.session.settings import SessionSettings
from unfazed.protocol import ASGIType
from unfazed.utils import import_string


class SessionMiddleware:
    def __init__(self, app: ASGIApplication):
        self.app = app

        self.setting: SessionSettings = settings["SESSION_SETTINGS"]
        self.engine_cls: t.Type[SessionBase] = import_string(self.setting.engine)

    async def __call__(
        self, scope: HTTPScope, receive: ASGISendCallable, send: ASGIReceiveCallable
    ):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)

        if self.setting.cookie_name in connection.cookies:
            session_key = connection.cookies[self.setting.cookie_name]
        else:
            session_key = None

        session_store: SessionBase = self.engine_cls(self.setting, session_key)
        scope["session"] = session_store

        async def wrapped_send(message: Message):
            if message["type"] == ASGIType.HTTP_RESPONSE_START:
                headers = MutableHeaders(scope=message)
                if session_store.modified:
                    headers.append("Set-Cookie", session_store.header_value)

            await send(message)

        await self.app(scope, receive, wrapped_send)
