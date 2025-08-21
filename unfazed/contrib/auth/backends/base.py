import typing as t
from abc import ABC, abstractmethod

from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.type import Doc, GenericReponse


class BaseAuthBackend(ABC):
    def __init__(self, options: t.Dict | None = None) -> None:
        self.options = options or {}

    @property
    @abstractmethod
    def alias(self) -> str: ...

    @abstractmethod
    async def login(
        self, ctx: LoginCtx
    ) -> t.Tuple[
        t.Annotated[
            t.Dict,
            Doc(description="session info, it will be set in the request.session"),
        ],
        t.Annotated[GenericReponse, Doc(description="response data")],
    ]: ...

    @abstractmethod
    async def session_info(
        self, user: AbstractUser, ctx: LoginCtx
    ) -> t.Dict[str, t.Any]: ...

    @abstractmethod
    async def register(self, ctx: RegisterCtx) -> None: ...

    @abstractmethod
    async def logout(self, session: t.Dict[str, t.Dict]) -> t.Any: ...

    @abstractmethod
    async def oauth_login_redirect(self) -> str: ...

    @abstractmethod
    async def oauth_logout_redirect(self) -> str: ...
