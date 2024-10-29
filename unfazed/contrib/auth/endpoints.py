import typing as t

from unfazed.http import HttpRequest, JsonResponse

from .const import SESSION_KEY
from .schema import LOGIN_RESPONSE, LoginCtx
from .services import UserService


async def login(
    request: HttpRequest, ctx: LoginCtx
) -> t.Annotated[JsonResponse, *LOGIN_RESPONSE]:
    ret, session_info = UserService.login(ctx)
    request.session[SESSION_KEY] = session_info
    return JsonResponse(ret)


async def logout(request: HttpRequest) -> JsonResponse:
    ret = UserService.logout()
    return JsonResponse(ret)
