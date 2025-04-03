import typing as t

import orjson as json
from starlette.requests import Request

if t.TYPE_CHECKING:
    from unfazed.contrib.auth.models import AbstractUser  # pragma: no cover
    from unfazed.contrib.session.backends.base import SessionBase  # pragma: no cover
    from unfazed.core import Unfazed  # pragma: no cover


class HttpRequest(Request):
    """
    Enhanced HTTP request class for the Unfazed framework.

    This class extends Starlette's Request class to provide additional functionality
    specific to the Unfazed framework, including JSON parsing, session management,
    user authentication, and application access.

    Attributes:
        _json (t.Dict): Cached JSON body of the request.

    Properties:
        scheme (str): The URL scheme (http/https).
        path (str): The URL path.
        session (SessionBase): The session object if SessionMiddleware is installed.
        user (AbstractUser): The authenticated user if AuthenticationMiddleware is installed.
        unfazed (Unfazed): The Unfazed application instance.

    Example:
        ```python
        from unfazed.http import HttpRequest, HttpResponse

        async def my_view(request: HttpRequest):
            # Parse JSON request body
            body = await request.json()

            # Access request metadata
            path = request.path
            scheme = request.scheme

            # Access session (requires SessionMiddleware)
            session = request.session

            # Access authenticated user (requires AuthenticationMiddleware)
            user = request.user

            # Access the Unfazed application
            unfazed = request.unfazed

            return HttpResponse(content="Hello, world")
        ```
    """

    @t.override
    async def json(self) -> t.Dict:
        """
        Parse the request body as JSON using orjson.

        This method caches the parsed JSON to avoid parsing the body multiple times.

        Returns:
            t.Dict: The parsed JSON body.

        Raises:
            json.JSONDecodeError: If the request body is not valid JSON.
        """
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json

    @property
    def scheme(self) -> str:
        """
        Get the URL scheme (http/https).

        Returns:
            str: The URL scheme.
        """
        return self.url.scheme

    @property
    def path(self) -> str:
        """
        Get the URL path.

        Returns:
            str: The URL path.
        """
        return self.url.path

    @property
    @t.override
    def session(self) -> "SessionBase":  # type: ignore
        """
        Get the session object.

        Returns:
            SessionBase: The session object.

        Raises:
            ValueError: If SessionMiddleware is not installed.
        """
        if "session" not in self.scope:
            raise ValueError(
                "SessionMiddleware must be installed to access request.session"
            )

        return self.scope["session"]

    @property
    @t.override
    def user(self) -> "AbstractUser":  # type: ignore
        """
        Get the authenticated user.

        Returns:
            AbstractUser: The authenticated user or None if not authenticated.

        Raises:
            ValueError: If AuthenticationMiddleware is not installed.
        """
        if "user" not in self.scope:
            raise ValueError(
                "AuthenticationMiddleware must be installed to access request.user"
            )
        return self.scope.get("user", None)

    @property
    def unfazed(self) -> "Unfazed":
        """
        Get the Unfazed application instance.

        Returns:
            Unfazed: The Unfazed application instance.
        """
        return self.scope["app"]
