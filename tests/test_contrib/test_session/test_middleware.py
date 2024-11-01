import uuid

from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.session.settings import SessionSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from unfazed.route import Route
from unfazed.test import Requestfactory

UNFAZED_SETTINGS = {
    "PROJECT": "test_middleware",
    "MIDDLEWARE": ["unfazed.contrib.session.middleware.SessionMiddleware"],
}

SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "garena.com",
    "COOKIE_SECURE": True,
}


async def set_session(request: HttpRequest) -> HttpResponse:
    request.session["TEST_MIDDLEWARE"] = {"foo": "bar"}

    return HttpResponse("ok")


async def update_session(request: HttpRequest) -> HttpResponse:
    request.session["TEST_MIDDLEWARE"] = {"foo2": "bar2"}

    return HttpResponse("ok")


async def read_session(request: HttpRequest) -> JsonResponse:
    if "TEST_MIDDLEWARE" in request.session:
        data = request.session["TEST_MIDDLEWARE"]
    else:
        data = {}
    return JsonResponse(data)


async def flush_session(request: HttpRequest) -> HttpResponse:
    await request.session.flush()

    return HttpResponse("ok")


ROUTES = [
    Route("/login", set_session),
    Route("/update", update_session),
    Route("/read", read_session),
    Route("/logout", flush_session),
]


async def test_middleware():
    unfazed = Unfazed(settings=UnfazedSettings(**UNFAZED_SETTINGS), routes=ROUTES)
    await unfazed.setup()
    settings["SESSION_SETTINGS"] = SessionSettings(**SESSION_SETTINGS)

    with Requestfactory(unfazed, base_url="https://garena.com") as request:
        # login
        resp = request.get("/login")
        assert resp.status_code == 200
        assert resp.text == "ok"

        # read
        resp = request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {"foo": "bar"}

        # update
        resp = request.get("/update")
        assert resp.status_code == 200
        assert resp.text == "ok"

        # read
        resp = request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {"foo2": "bar2"}

        # flush
        resp = request.get("/logout")
        assert resp.status_code == 200
        assert resp.text == "ok"

        # read
        resp = request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {}
