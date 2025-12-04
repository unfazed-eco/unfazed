import os

from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import Route, include, mount, path, static


async def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse("hello, world")


def get_static_dir() -> str:
    relative_path = os.path.join(os.path.dirname(__file__), "../../staticfiles")
    return os.path.abspath(relative_path)


patterns = [
    path("/path", routes=include("route_common.routes")),
    static("/static", get_static_dir()),
    static("/static_html", get_static_dir(), html=True),
    mount(
        "/mount/app",
        app=Unfazed(routes=[Route("/bar", endpoint=hello)]),
    ),
    mount("/mount/route", routes=[Route("/bar", endpoint=hello)]),
]
