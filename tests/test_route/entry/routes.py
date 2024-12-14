from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import include, path


async def foo(request: HttpRequest) -> HttpResponse:
    return HttpResponse("hello, world")


patterns = [
    path("/api/success", routes=include("route_common.routes")),
    path("/api/mainapp/foo", endpoint=foo),
]
