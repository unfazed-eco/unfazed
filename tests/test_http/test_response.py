from unfazed.http import HttpResponse, JsonResponse, PlainTextResponse, RedirctResponse


def test_httpresponse():
    resp = HttpResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"

    resp = PlainTextResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"


def test_jsonresponse():
    content = {"a": 1}
    resp = JsonResponse(content=content)

    assert resp.body == b'{"a":1}'
    assert resp.media_type == "application/json"


def test_redirctresponse():
    resp = RedirctResponse(url="/api")
    assert resp.headers["location"] == "/api"
    assert resp.status_code == 302
