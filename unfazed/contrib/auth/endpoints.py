import typing as t

from unfazed.conf import settings
from unfazed.http import HttpRequest, JsonResponse
from unfazed.utils import generic_response

from .schema import LOGIN_RESPONSE, LoginCtx, RegisterCtx
from .services import AuthService
from .settings import UnfazedContribAuthSettings

_ = t.Annotated


async def login(
    request: HttpRequest, ctx: LoginCtx
) -> _[JsonResponse, *LOGIN_RESPONSE]:
    s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]
    session_info, ret = await s.login(ctx)
    request.session[auth_settings.SESSION_KEY] = session_info
    return generic_response(ret)


async def logout(request: HttpRequest) -> JsonResponse:
    s = AuthService()
    ret = await s.logout(request.session)
    await request.session.flush()
    return generic_response(ret)


async def register(request: HttpRequest, ctx: RegisterCtx) -> JsonResponse:
    s = AuthService()
    ret = await s.register(ctx)
    return generic_response(ret)
