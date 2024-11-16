import typing as t
from functools import lru_cache

from unfazed.conf import settings
from unfazed.contrib.auth.backends.base import BaseAuthBackend
from unfazed.contrib.auth.settings import UnfazedContribAuthSettings
from unfazed.http import HttpRequest
from unfazed.type import Doc
from unfazed.utils import import_string

from .schema import LoginCtx, RegisterCtx


@lru_cache
def _load_backends(
    auth_setting: UnfazedContribAuthSettings,
) -> t.Dict[str, BaseAuthBackend]:
    ret = {}
    for alias, backend_config in auth_setting.BACKENDS.items():
        backend_cls = import_string(backend_config.BACKEND_CLS)
        backend = backend_cls(backend_config.OPTIONS)
        if backend.alias != alias:
            raise ValueError(
                f"Unfazed Error: AuthBackend {backend_cls} alias {backend.alias} not match with {alias}"
            )
        ret[alias] = backend

    return ret


class AuthHandler:
    def __init__(self, request: HttpRequest) -> None:
        self.settings: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]
        self.request = request
        self.backends = _load_backends(self.settings)

    def choose_backend(
        self, backend: str
    ) -> t.Annotated[
        BaseAuthBackend, Doc(description="backend that inherits from BaseAuthBackend")
    ]:
        if backend not in self.backends:
            raise ValueError(f"Unfazed Error: AuthBackend {backend} not found")

        return self.backends[backend]

    async def authenticate(self, ctx: LoginCtx) -> t.Any:
        backend = self.choose_backend(ctx.platform)
        user = await backend.authenticate(ctx)
        ret = await backend.login(self.request, user)
        return ret

    async def logout(self) -> None:
        self.request.session.flush()

    async def register(self, ctx: RegisterCtx) -> t.Any:
        backend = self.choose_backend(ctx.platform)
        ret = await backend.register(ctx)
        return ret
