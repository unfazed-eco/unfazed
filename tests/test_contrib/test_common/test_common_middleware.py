from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import Route
from unfazed.test import Requestfactory


async def endpoint1(request: HttpRequest) -> JsonResponse:
    raise ValueError("error")


async def endpoint2(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"foo": "bar"})


async def endpoint3(request: HttpRequest) -> JsonResponse:
    raise PermissionDenied()


_SETTINGS = {
    "DEBUG": True,
    "MIDDLEWARE": ["unfazed.contrib.common.middleware.CommonMiddleware"],
}


async def test_common_middleware() -> None:
    unfazed = Unfazed(
        settings=UnfazedSettings.model_validate(_SETTINGS),
        routes=[
            Route("/foo", endpoint=endpoint1),
            Route("/bar", endpoint=endpoint2),
            Route("/baz", endpoint=endpoint3),
        ],
    )

    await unfazed.setup()

    async with Requestfactory(app=unfazed) as request:
        resp1 = await request.get("/foo")
        assert resp1.status_code == 200
        assert resp1.json() == {
            "code": 500,
            "message": "error",
            "data": {},
        }

        resp2 = await request.get("/bar")
        assert resp2.status_code == 200
        assert resp2.json() == {"foo": "bar"}

        resp3 = await request.get("/baz")
        assert resp3.status_code == 200
        assert resp3.json() == {
            "code": 403,
            "message": "Permission Denied",
            "data": {},
        }
