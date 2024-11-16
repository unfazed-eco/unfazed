import typing as t

from pydantic import BaseModel

from unfazed.http import HttpRequest, HttpResponse, JsonResponse

from .schema import LOGIN_RESPONSE, LoginCtx
from .services import AuthService

_ = t.Annotated


def generic_response(ret: t.Any) -> HttpResponse:
    if isinstance(ret, HttpResponse):
        return ret
    elif isinstance(ret, (t.Dict, BaseModel)):
        return JsonResponse(ret)
    else:
        return HttpResponse(ret)


async def login(
    request: HttpRequest, ctx: LoginCtx
) -> _[JsonResponse, *LOGIN_RESPONSE]:
    ret = AuthService.login(request, ctx)

    return generic_response(ret)


async def logout(request: HttpRequest) -> JsonResponse:
    ret = AuthService.logout(request)
    return generic_response(ret)


async def register(request: HttpRequest) -> JsonResponse:
    ret = AuthService.register(request)
    return generic_response(ret)


# Redirects for oauth
async def login_redirect(request: HttpRequest) -> JsonResponse:
    ret = AuthService.login_redirect(request)
    return generic_response(ret)


async def logout_redirect(request: HttpRequest) -> JsonResponse:
    ret = AuthService.logout_redirect(request)
    return generic_response(ret)
