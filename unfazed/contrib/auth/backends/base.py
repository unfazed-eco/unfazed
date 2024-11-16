import typing as t

from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.schema import LoginCtx
from unfazed.http import HttpRequest, HttpResponse


class BaseAuthBackend:
    def __init__(self, options: t.Dict) -> None:
        self.options = options

    @property
    def alias(self) -> str:
        raise NotImplementedError

    # login
    async def authenticate(self, ctx: LoginCtx) -> HttpResponse:
        raise NotImplementedError

    async def login(
        self, request: HttpRequest, user: AbstractUser, session_key: str
    ) -> t.Any:
        session_info = {
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
        }
        request.session[session_key] = session_info

        return session_info

    async def register(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    async def logout(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    def get_signin_url(self, request: HttpRequest) -> str:
        raise NotImplementedError

    def get_signout_url(self, request: HttpRequest) -> str:
        raise NotImplementedError
