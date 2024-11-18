import typing as t

from unfazed.http import HttpRequest, JsonResponse
from unfazed.utils import generic_response

from .schema import LOGIN_RESPONSE, LoginCtx, RegisterCtx
from .services import AuthService

_ = t.Annotated


async def login(
    request: HttpRequest, ctx: LoginCtx
) -> _[JsonResponse, *LOGIN_RESPONSE]:
    s = AuthService(request)
    ret = await s.login(ctx)

    return generic_response(ret)


async def logout(request: HttpRequest) -> JsonResponse:
    s = AuthService(request)
    ret = s.logout()
    return generic_response(ret)


async def register(request: HttpRequest, ctx: RegisterCtx) -> JsonResponse:
    s = AuthService(request)
    ret = await s.register(ctx)
    return generic_response(ret)


# Redirects for oauth
# async def login_redirect(request: HttpRequest) -> RedirctResponse:
#     s = AuthService(request)
#     ret = s.login_redirect(request)
#     return generic_response(ret)


# async def logout_redirect(request: HttpRequest) -> JsonResponse:
#     s = AuthService(request)
#     ret = s.logout_redirect(request)
#     return generic_response(ret)
