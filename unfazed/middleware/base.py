from abc import ABC, abstractmethod

from unfazed.type import ASGIApp, Receive, Scope, Send


class BaseMiddleware(ABC):
    """
    Base Middleware Class


    Usage:

    ```python


    class CommonMiddleware(BaseMiddleware):

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return

            await self.app(scope, receive, send)

    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
