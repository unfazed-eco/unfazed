import pytest

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.lifespan import BaseLifeSpan, lifespan_handler
from unfazed.route.routing import Route
from unfazed.test import Requestfactory


@pytest.fixture(autouse=True)
def setup_requestfactory_env():
    lifespan_handler.clear()
    yield


async def endpoint1(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")


class LifeSpanStartFailed(BaseLifeSpan):
    async def on_startup(self):
        raise RuntimeError("LifeSpanStartFailed")


class LifeSpanShutdownFailed(BaseLifeSpan):
    async def on_shutdown(self):
        raise RuntimeError("LifeSpanShutdownFailed")


async def test_requestfactory():
    unfazed = Unfazed(
        routes=[Route("/", endpoint=endpoint1)],
        settings=UnfazedSettings(
            DEBUG=True,
        ),
    )
    await unfazed.setup()

    async with Requestfactory(unfazed) as request:
        resp = await request.get("/")
        assert resp.status_code == 200


async def test_requestfactory_startup_failed():
    unfazed = Unfazed(
        routes=[Route("/", endpoint=endpoint1)],
        settings=UnfazedSettings(
            DEBUG=True,
            LIFESPAN=["tests.test_test.test_requestfactory.LifeSpanStartFailed"],
        ),
    )

    await unfazed.setup()

    with pytest.raises(RuntimeError):
        async with Requestfactory(unfazed) as request:
            await request.get("/")


async def test_requestfactory_shutdown_failed():
    unfazed = Unfazed(
        routes=[Route("/", endpoint=endpoint1)],
        settings=UnfazedSettings(
            DEBUG=True,
            LIFESPAN=["tests.test_test.test_requestfactory.LifeSpanShutdownFailed"],
        ),
    )

    await unfazed.setup()
    with pytest.raises(RuntimeError):
        async with Requestfactory(unfazed) as request:
            await request.get("/")
