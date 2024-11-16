import typing as t

from unfazed.http import HttpRequest

from .handler import AuthCenter
from .schema import LoginCtx, RegisterCtx


class AuthService:
    @classmethod
    def login(cls, request: HttpRequest, ctx: LoginCtx) -> t.Any:
        ac = AuthCenter(request)
        ret = ac.authenticate(ctx)

        return ret

    @classmethod
    def logout(cls, request: HttpRequest) -> t.Any:
        ac = AuthCenter(request)
        ret = ac.logout()

        return ret

    @classmethod
    def register(cls, request: HttpRequest, ctx: RegisterCtx) -> t.Any:
        ac = AuthCenter(request)
        ret = ac.register(ctx)

        return ret

    @classmethod
    def login_redirect(cls, request: HttpRequest) -> t.Any:
        ac = AuthCenter(request)
        ret = ac.login_redirect()

        return ret

    @classmethod
    def logout_redirect(cls, request: HttpRequest) -> t.Any:
        ac = AuthCenter(request)
        ret = ac.logout_redirect()

        return ret
