import typing as t

from unfazed.conf import settings
from unfazed.http import HttpRequest, HttpResponse, JsonResponse, RedirectResponse
from unfazed.route import params as p

from . import schema as s
from .services import AuthService
from .settings import UnfazedContribAuthSettings


async def login(
    request: HttpRequest,
    ctx: t.Annotated[s.LoginCtx, p.Json()],
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.LoginSucceedResponse)]:
    a_s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]
    session_info, ret = await a_s.login(ctx)
    request.session[auth_settings.SESSION_KEY] = session_info
    return JsonResponse(s.LoginSucceedResponse(data=ret))


async def logout(
    request: HttpRequest,
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.LogoutSucceedResponse)]:
    a_s = AuthService()
    auth_settings: UnfazedContribAuthSettings = settings[
        "UNFAZED_CONTRIB_AUTH_SETTINGS"
    ]

    if auth_settings.SESSION_KEY not in request.session:
        return JsonResponse(s.LogoutSucceedResponse(data={}))
    else:
        ret = await a_s.logout(request.session[auth_settings.SESSION_KEY])
        # only delete auth_settings.SESSION_KEY
        del request.session[auth_settings.SESSION_KEY]
        return JsonResponse(s.LogoutSucceedResponse(data=ret))


async def register(
    request: HttpRequest,
    ctx: t.Annotated[s.RegisterCtx, p.Json()],
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.RegisterSucceedResponse)]:
    a_s = AuthService()
    ret = await a_s.register(ctx)
    return JsonResponse(s.RegisterSucceedResponse(data=ret))


async def oauth_login_redirect(
    request: HttpRequest, platform: str
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.RedirectUrlResponse)]:
    a_s = AuthService()
    ret = await a_s.oauth_login_redirect(platform)
    return RedirectResponse(ret)


async def oauth_logout_redirect(
    request: HttpRequest, platform: str
) -> t.Annotated[HttpResponse, p.ResponseSpec(model=s.RedirectUrlResponse)]:
    a_s = AuthService()
    ret = await a_s.oauth_logout_redirect(platform)
    return RedirectResponse(ret)
