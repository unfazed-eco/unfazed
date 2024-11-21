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


class AuthService:
    def __init__(self, request: HttpRequest) -> None:
        self.auth_settings: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]
        self.request = request
        self.backends = _load_backends(self.auth_settings)

    def choose_backend(
        self, backend: str
    ) -> t.Annotated[
        BaseAuthBackend, Doc(description="backend that inherits from BaseAuthBackend")
    ]:
        if backend not in self.backends:
            raise ValueError(f"Unfazed Error: AuthBackend {backend} not found")

        return self.backends[backend]

    async def login(self, ctx: LoginCtx) -> t.Any:
        backend = self.choose_backend(ctx.platform)
        session_info, resp = await backend.login(ctx)
        self.request.session[self.auth_settings.SESSION_KEY] = session_info
        return resp

    async def logout(self) -> None:
        self.request.session.flush()

    async def register(self, ctx: RegisterCtx) -> t.Any:
        backend = self.choose_backend(ctx.platform)
        ret = await backend.register(ctx)
        return ret

    def login_redirect(self, request: HttpRequest) -> t.Any:
        # backend = self.choose_backend(request.GET.get("platform", "default"))
        # return backend.login_redirect(request)
        # TODO: implement login_redirect
        pass

    def logout_redirect(self, request: HttpRequest) -> t.Any:
        # backend = self.choose_backend(request.GET.get("platform", "default"))
        # return backend.logout_redirect(request)
        # TODO: implement logout_redirect
        pass
