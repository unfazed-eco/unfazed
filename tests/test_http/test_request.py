from unfazed.http import HttpRequest


async def test_http_request() -> None:
    http_scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api",
        "query_string": b"",
        "headers": [
            (b"host", b"localhost"),
            (b"user-agent", b"Mozilla/5.0"),
        ],
    }

    request = HttpRequest(http_scope)
    request._body = b'{"a": 1}'

    assert request.scheme == "http"
    assert request.path == "/api"

    assert await request.json() == {"a": 1}
