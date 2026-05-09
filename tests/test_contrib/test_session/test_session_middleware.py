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
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "test_middleware",
            "OPTIONS": {
                "PREFIX": "test_middleware",
            },
        },
    },
}


DEFAULT_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
}

CACHE_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
    "CACHE_ALIAS": "default",
    "ENGINE": "unfazed.contrib.session.backends.cache.CacheSession",
}

BROWSER_CLOSE_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
    "COOKIE_EXPIRE_AT_BROWSER_CLOSE": True,
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


async def _build_unfazed() -> Unfazed:
    unfazed = Unfazed(
        settings=UnfazedSettings.model_validate(UNFAZED_SETTINGS),
        routes=ROUTES,
        silent=True,
    )
    await unfazed.setup()
    return unfazed


def _assert_persistent_session_cookie(header_value: str | None) -> None:
    assert header_value is not None
    assert "Max-Age=604800" in header_value
    assert "expires=" not in header_value.lower()


def _assert_browser_close_session_cookie(header_value: str | None) -> None:
    assert header_value is not None
    assert "Max-Age" not in header_value
    assert "expires=" not in header_value.lower()


def _assert_deleted_session_cookie(header_value: str | None) -> None:
    assert header_value is not None
    assert "Max-Age=0" in header_value
    assert "expires=Thu, 01 Jan 1970 00:00:00 GMT" in header_value
    assert "expires=expires=" not in header_value


async def _test_engine(
    unfazed: Unfazed,
    session_setting: SessionSettings,
    *,
    expire_at_browser_close: bool = False,
) -> None:
    settings["UNFAZED_CONTRIB_SESSION_SETTINGS"] = session_setting

    async with Requestfactory(unfazed, base_url="https://unfazed.com") as request:
        # login
        resp = await request.get("/login")
        assert resp.status_code == 200
        assert resp.text == "ok"
        if expire_at_browser_close:
            _assert_browser_close_session_cookie(resp.headers.get("set-cookie"))
        else:
            _assert_persistent_session_cookie(resp.headers.get("set-cookie"))

        # read
        resp = await request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {"foo": "bar"}

        # update
        resp = await request.get("/update")
        assert resp.status_code == 200
        assert resp.text == "ok"
        if expire_at_browser_close:
            _assert_browser_close_session_cookie(resp.headers.get("set-cookie"))
        else:
            _assert_persistent_session_cookie(resp.headers.get("set-cookie"))

        # read
        resp = await request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {"foo2": "bar2"}

        # flush
        resp = await request.get("/logout")
        assert resp.status_code == 200
        assert resp.text == "ok"
        _assert_deleted_session_cookie(resp.headers.get("set-cookie"))

        # read
        resp = await request.get("/read")
        assert resp.status_code == 200
        assert resp.json() == {}


async def test_middleware() -> None:
    await _test_engine(
        await _build_unfazed(),
        SessionSettings.model_validate(BROWSER_CLOSE_SESSION_SETTINGS),
        expire_at_browser_close=True,
    )

    await _test_engine(
        await _build_unfazed(),
        SessionSettings.model_validate(DEFAULT_SESSION_SETTINGS),
    )

    await _test_engine(
        await _build_unfazed(),
        SessionSettings.model_validate(CACHE_SESSION_SETTINGS)
    )
