import typing as t

from unfazed.conf import settings
from unfazed.http import HttpRequest, HttpResponse
from unfazed.utils import generic_response

from .schema import LOGIN_RESPONSE, LoginCtx, RegisterCtx
from .services import AuthService
from .settings import UnfazedContribAuthSettings


async def login(
    request: HttpRequest, ctx: LoginCtx
) -> t.Annotated[HttpResponse, *LOGIN_RESPONSE]:
    s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]
    session_info, ret = await s.login(ctx)
    request.session[auth_settings.SESSION_KEY] = session_info
    return generic_response(ret)


async def logout(request: HttpRequest) -> HttpResponse:
    s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]

    if auth_settings.SESSION_KEY not in request.session:
        return generic_response({})
    else:
        ret = await s.logout(request.session[auth_settings.SESSION_KEY])
        # only delete auth_settings.SESSION_KEY
        del request.session[auth_settings.SESSION_KEY]
        return generic_response(ret)


async def register(request: HttpRequest, ctx: RegisterCtx) -> HttpResponse:
    s = AuthService()
    ret = await s.register(ctx)
    return generic_response(ret)
