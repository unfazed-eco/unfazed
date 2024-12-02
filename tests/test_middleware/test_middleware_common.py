from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route.routing import Route
from unfazed.test import Requestfactory


async def endpoint1(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")


async def endpoint2(request: HttpRequest) -> HttpResponse:
    raise ValueError("Error")


_Settings = {
    "DEBUG": True,
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}

_Settings2 = {
    "DEBUG": False,
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}


async def test_middleware_common():
    unfazed = Unfazed(
        settings=UnfazedSettings(**_Settings),
        routes=[
            Route("/enpoint1", endpoint=endpoint1),
            Route("/enpoint2", endpoint=endpoint2),
        ],
    )

    await unfazed.setup()

    async with Requestfactory(unfazed) as request:
        response = await request.get("/enpoint1")
        assert response.status_code == 200

        response = await request.get("/enpoint2")
        assert response.status_code == 500

    unfazed2 = Unfazed(
        settings=UnfazedSettings(**_Settings2),
        routes=[
            Route("/enpoint1", endpoint=endpoint1),
            Route("/enpoint2", endpoint=endpoint2),
        ],
    )

    await unfazed2.setup()

    async with Requestfactory(unfazed2) as request:
        response = await request.get("/enpoint2")
        assert response.status_code == 500
