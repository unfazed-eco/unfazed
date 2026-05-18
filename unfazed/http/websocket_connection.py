import typing as t

from starlette.websockets import WebSocket

if t.TYPE_CHECKING:  # pragma: no cover
    from unfazed.contrib.session.backends.base import SessionBase
    from unfazed.core import Unfazed


class WebSocketConnection(WebSocket):
    """
    Enhanced WebSocket connection class for the Unfazed framework.

    Extends Starlette's WebSocket to provide framework-specific functionality
    including session access, user authentication, and application reference.

    Properties inherited from HTTPConnection (via WebSocket):
        url, headers, cookies, query_params, path_params, client, base_url

    Properties added by WebSocketConnection:
        scheme: The URL scheme (ws/wss).
        session: The session object (requires SessionMiddleware).
        user: The authenticated user (requires AuthenticationMiddleware).
        unfazed: The Unfazed application instance.

    Example:
        ```python
        from unfazed.http import WebSocketConnection

        async def chat(ws: WebSocketConnection, room_id: str) -> None:
            await ws.accept()
            try:
                while True:
                    data = await ws.receive_json()
                    user = ws.user
                    await ws.send_json({"room": room_id, "user": user, "echo": data})
            except WebSocketDisconnect:
                pass
        ```
    """

    @property
    def scheme(self) -> str:
        """Get the URL scheme (ws or wss)."""
        return self.url.scheme

    @property
    @t.override
    def session(self) -> "SessionBase":  # type: ignore[override]
        """
        Get the session object.

        Raises:
            ValueError: If SessionMiddleware is not installed.
        """
        if "session" not in self.scope:
            raise ValueError(
                "SessionMiddleware must be installed to access websocket.session"
            )
        return self.scope["session"]  # pragma: no cover

    @property
    @t.override
    def user(self) -> t.Any:
        """
        Get the authenticated user.

        Raises:
            ValueError: If AuthenticationMiddleware is not installed.
        """
        if "user" not in self.scope:
            raise ValueError(
                "AuthenticationMiddleware must be installed to access websocket.user"
            )
        return self.scope.get("user", None)  # pragma: no cover

    @property
    def unfazed(self) -> "Unfazed":
        """Get the Unfazed application instance."""
        return self.scope["app"]
