import typing as t

from unfazed.conf import settings
from unfazed.contrib.auth.backends.base import BaseAuthBackend
from unfazed.type import Doc
from unfazed.utils import import_string

from .schema import LoginCtx, RegisterCtx
from .settings import UnfazedContribAuthSettings


def load_backends(
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
    def __init__(self) -> None:
        self.backends = load_backends(settings["UNFAZED_CONTRIB_AUTH_SETTINGS"])

    def choose_backend(
        self, backend: str
    ) -> t.Annotated[
        BaseAuthBackend, Doc(description="backend inherited from BaseAuthBackend")
    ]:
        if backend not in self.backends:
            backend = "default"

        return self.backends[backend]

    async def login(self, ctx: LoginCtx) -> t.Tuple[t.Dict, t.Any]:
        backend = self.choose_backend(ctx.platform)
        session_info, resp = await backend.login(ctx)
        return session_info, resp

    async def logout(self, session: t.Dict) -> t.Any:
        if "platform" in session:
            platform = session["platform"]
        else:
            platform = "default"
        backend = self.choose_backend(platform)
        resp = await backend.logout(session)
        return resp

    async def register(self, ctx: RegisterCtx) -> t.Any:
        backend = self.choose_backend(ctx.platform)
        ret = await backend.register(ctx)
        return ret
