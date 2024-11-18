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
    async def login(self, ctx: LoginCtx) -> t.Tuple[t.Dict, t.Any]:
        raise NotImplementedError

    async def session_info(
        self, user: AbstractUser, ctx: LoginCtx
    ) -> t.Dict[str, t.Any]:
        session_info = {
            "id": user.id,
            "account": user.account,
            "email": user.email,
            "is_superuser": user.is_superuser,
        }

        return session_info

    async def register(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    async def logout(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    def get_signin_url(self, request: HttpRequest) -> str:
        raise NotImplementedError

    def get_signout_url(self, request: HttpRequest) -> str:
        raise NotImplementedError
