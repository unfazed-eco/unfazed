import typing as t

from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection

from unfazed.conf import settings
from unfazed.contrib.session.backends.base import SessionBase
from unfazed.contrib.session.settings import SessionSettings
from unfazed.contrib.session.utils import build_cookie
from unfazed.protocol import ASGIType
from unfazed.type import ASGIApp, Message, Receive, Scope, Send
from unfazed.utils import import_string


class SessionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

        self.setting: SessionSettings = settings["UNFAZED_CONTRIB_SESSION_SETTINGS"]
        self.engine_cls: t.Type[SessionBase] = import_string(self.setting.engine)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)

        if self.setting.cookie_name in connection.cookies:
            session_key = connection.cookies[self.setting.cookie_name]
        else:
            session_key = None

        session_store: SessionBase = self.engine_cls(self.setting, session_key)
        await session_store.load()
        scope["session"] = session_store

        async def wrapped_send(message: Message) -> None:
            if message["type"] == ASGIType.HTTP_RESPONSE_START:
                headers = MutableHeaders(scope=message)

                # if session is created / updated / deleted
                # save the session and reset the cookie
                if session_store.modified:
                    await session_store.save()

                    # if session is empty, delete the cookie
                    if session_store:
                        header_value = build_cookie(
                            self.setting.cookie_name,
                            t.cast(str, session_store.session_key),
                            max_age=self.setting.cookie_max_age,
                            expires=session_store.get_expiry_age(),
                            path=self.setting.cookie_path,
                            domain=self.setting.cookie_domain,
                            secure=self.setting.cookie_secure,
                            httponly=self.setting.cookie_httponly,
                            samesite=self.setting.cookie_samesite,
                        )
                    else:
                        header_value = build_cookie(
                            self.setting.cookie_name,
                            "null",
                            max_age=0,
                            expires=session_store.get_expiry_age(),
                            path=self.setting.cookie_path,
                            domain=self.setting.cookie_domain,
                            secure=self.setting.cookie_secure,
                            httponly=self.setting.cookie_httponly,
                            samesite=self.setting.cookie_samesite,
                        )
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, wrapped_send)
