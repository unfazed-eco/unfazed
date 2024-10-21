from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import path


async def foo(request: HttpRequest) -> HttpResponse:
    return HttpResponse("hello, world")


patterns = [path("/foo", endpoint=foo)]
