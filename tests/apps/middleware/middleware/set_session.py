from starlette.types import Receive, Scope, Send

from unfazed.middleware import BaseMiddleware


class SetSessionMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        scope["session"] = "session.test"

        await self.app(scope, receive, send)
