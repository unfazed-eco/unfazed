import os

from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import include, path, static


async def foo(request: HttpRequest) -> HttpResponse:
    return HttpResponse("hello, world")


def get_static_dir() -> str:
    relative_path = os.path.join(os.path.dirname(__file__), "../../staticfiles")
    return os.path.abspath(relative_path)


patterns = [
    path("/api/success", routes=include("route_common.routes")),
    path("/api/mainapp/foo", endpoint=foo),
    static("/static", get_static_dir()),
]
