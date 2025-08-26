import typing as t

from unfazed.conf import settings
from unfazed.http import HttpRequest, HttpResponse, RedirectResponse
from unfazed.route import params as p
from unfazed.utils import generic_response

from . import schema as s
from .services import AuthService
from .settings import UnfazedContribAuthSettings


async def login(
    request: HttpRequest,
    ctx: t.Annotated[s.LoginCtx, p.Json()],
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.LoginSucceedResponse)]:
    s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]
    session_info, ret = await s.login(ctx)
    request.session[auth_settings.SESSION_KEY] = session_info
    return generic_response(ret)


async def logout(
    request: HttpRequest,
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.LogoutSucceedResponse)]:
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


async def register(
    request: HttpRequest,
    ctx: t.Annotated[s.RegisterCtx, p.Json()],
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.RegisterSucceedResponse)]:
    s = AuthService()
    ret = await s.register(ctx)
    return generic_response(ret)


async def oauth_login_redirect(request: HttpRequest, platform: str) -> RedirectResponse:
    s = AuthService()
    ret = await s.oauth_login_redirect(platform)
    return RedirectResponse(ret)


async def oauth_logout_redirect(
    request: HttpRequest, platform: str
) -> RedirectResponse:
    s = AuthService()
    ret = await s.oauth_logout_redirect(platform)
    return RedirectResponse(ret)
