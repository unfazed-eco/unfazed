import asyncio
import os
import typing as t

import pytest
from pydantic import BaseModel
from starlette.background import BackgroundTask

from unfazed.http import (
    FileResponse,
    HtmlResponse,
    HttpResponse,
    JsonResponse,
    PlainTextResponse,
    RedirctResponse,
    StreamingResponse,
)
from unfazed.http.response import RangeFileHandler, parse_request


def test_str_esponse():
    resp = HttpResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"

    resp = PlainTextResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"

    resp = HtmlResponse(content="<h1>hello, world</h1>")
    assert resp.body == b"<h1>hello, world</h1>"
    assert resp.media_type == "text/html"


def test_jsonresponse():
    content = {"a": 1}
    resp = JsonResponse(content=content)

    assert resp.body == b'{"a":1}'
    assert resp.media_type == "application/json"

    class User(BaseModel):
        name: str
        age: int

    user = User(name="tom", age=18)
    resp = JsonResponse(content=user)
    assert resp.body == b'{"name":"tom","age":18}'

    with pytest.raises(ValueError):
        resp = JsonResponse(content="hello, world")


def test_redirctresponse():
    resp = RedirctResponse(url="/api")
    assert resp.headers["location"] == "/api"
    assert resp.status_code == 302


class StreamingApp:
    def __init__(self):
        self.event = asyncio.Event()
        self.body = b""

    async def send(self, msg: t.Dict[str, t.Any]):
        flag = "more_body" in msg and msg["more_body"] is False
        body = msg.get("body", b"")

        self.body += body

        if flag:
            self.event.set()

    async def reiceive(self):
        await self.event.wait()

        return {"type": "http.disconnect"}


async def test_streamingresponse():
    async def asynccontent():
        yield b"hello, "
        yield b"world"

    def synccontent():
        yield b"hello, "
        yield b"world"

    def strcontent():
        yield "hello, "
        yield "world"

    app1 = StreamingApp()
    resp = StreamingResponse(
        content=asynccontent(), background=BackgroundTask(asyncio.sleep, 0.1)
    )

    await resp({}, app1.reiceive, app1.send)

    assert app1.body == b"hello, world"

    app2 = StreamingApp()
    resp = StreamingResponse(content=synccontent())
    await resp({}, app2.reiceive, app2.send)
    assert app2.body == b"hello, world"

    app3 = StreamingApp()
    resp = StreamingResponse(content=strcontent())
    await resp({}, app3.reiceive, app3.send)
    assert app3.body == b"hello, world"


async def test_fileresponse():
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")

    _handler = RangeFileHandler(file_path)

    resp = FileResponse(
        file_path, headers={"If-Range": _handler.etag, "Range": "bytes=0-"}
    )

    total_length = 0
    with open(file_path, "rb") as f:
        content = f.read()
        total_length = len(content)

    # test header
    assert resp.headers["content-type"] == "application/octet-stream"
    assert resp.headers["content-length"] == str(total_length)
    assert "ETag" in resp.headers
    assert "Accept-Ranges" in resp.headers
    assert "Last-Modified" in resp.headers
    assert "Content-Disposition" in resp.headers

    app1 = StreamingApp()
    await resp({}, app1.reiceive, app1.send)

    body_str = app1.body.decode("utf-8")
    assert "Beautiful is better than ugly." in body_str
    assert (
        "Namespaces are one honking great idea -- let's do more of those!" in body_str
    )


def test_rangehandler():
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")

    stat = os.stat(file_path)

    with pytest.raises(FileNotFoundError):
        RangeFileHandler("notfound")

    handler = RangeFileHandler(file_path)

    assert handler.file_name == "zenofpython.txt"
    assert handler.file_size == stat.st_size
    assert handler.content_length == stat.st_size
    assert handler.last_modified is not None

    handler.set_range(0, 10)
    assert handler.range_start == 0
    assert handler.range_end == 10
    assert handler.content_length == 10
    assert handler.content_range == f"bytes 0-9/{stat.st_size}"


def test_fileresponse_parse_request():
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")

    handler = RangeFileHandler(file_path)

    req_headers = {
        "Range": "bytes=0-10",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)

    assert start == 0
    assert end == 10
    assert code == 206

    req_headers = {
        "Range": "bytes =-10",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)
    assert start == 0
    assert end == 10
    assert code == 206

    req_headers = {
        "Range": "bytes=",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)
    assert start == 0
    assert end == handler.file_size
    assert code == 206

    req_headers = {
        "Range": "bytes=x-y",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)
    assert start == 0
    assert end == handler.file_size
    assert code == 200

    req_headers = {
        "Range": "bytes=10-5",
        "If-Range": handler.etag,
    }
    start, end, code = parse_request(handler, req_headers)
    assert code == 416

    req_headers = {
        "Range": "bytes=10-5",
        "If-Range": "notfound",
    }
    start, end, code = parse_request(handler, req_headers)
    assert code == 200
    assert start == 0
    assert end == handler.file_size

    req_headers = {
        "Range": "bytes=10-",
        "If-Range": handler.etag,
    }
    start, end, code = parse_request(handler, req_headers)
    assert code == 206
    assert start == 10
    assert end == handler.file_size
