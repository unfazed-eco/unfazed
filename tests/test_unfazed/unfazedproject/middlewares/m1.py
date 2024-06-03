from unfazed.types import ASGIApp, Receive, Scope, Send


class CustomMiddleware1:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        await self.app(scope, receive, send)
