from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import path


async def foo(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello World!"})


async def bar(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello Bar!"})


async def subbar1(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello Bar2!"})


async def subbar2(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello Bar3!"})


_routes = [
    path("/subbar1", endpoint=subbar1),
    path("/subbar2", endpoint=subbar2),
]

patterns = [path("/foo", endpoint=foo), path("/bar", routes=_routes)]
