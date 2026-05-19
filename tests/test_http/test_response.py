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
    RedirectResponse,
    StreamingResponse,
)
from unfazed.http.response import (
    ByteRange,
    MultipartRangeFileHandler,
    RangeFileHandler,
    parse_request,
)


def test_str_esponse() -> None:
    resp = HttpResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"

    resp = PlainTextResponse(content="hello, world")
    assert resp.body == b"hello, world"
    assert resp.media_type == "text/plain"

    resp = HtmlResponse(content="<h1>hello, world</h1>")
    assert resp.body == b"<h1>hello, world</h1>"
    assert resp.media_type == "text/html"


def test_jsonresponse() -> None:
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
        resp = JsonResponse(content="hello, world")  # type: ignore


def test_RedirectResponse() -> None:
    resp = RedirectResponse(url="http://example.com/api")
    assert resp.headers["location"] == "http://example.com/api"
    assert resp.status_code == 302

    with pytest.raises(ValueError):
        RedirectResponse(url="/api")


class StreamingApp:
    def __init__(self) -> None:
        self.event = asyncio.Event()
        self.body = b""
        self.status_code = 0
        self.headers: dict[str, str] = {}

    async def send(self, msg: t.MutableMapping[str, t.Any]) -> None:
        if msg["type"] == "http.response.start":
            self.status_code = msg["status"]
            self.headers = {
                key.decode("latin-1"): value.decode("latin-1")
                for key, value in msg["headers"]
            }
            return

        flag = "more_body" in msg and msg["more_body"] is False
        body = msg.get("body", b"")

        self.body += body

        if flag:
            self.event.set()

    async def reiceive(self) -> t.Dict[str, str]:
        await self.event.wait()

        return {"type": "http.disconnect"}


async def test_streamingresponse() -> None:
    async def asynccontent() -> t.AsyncGenerator[bytes, None]:
        yield b"hello, "
        yield b"world"

    def synccontent() -> t.Generator[bytes, bytes, None]:
        yield b"hello, "
        yield b"world"

    def strcontent() -> t.Generator[str, str, None]:
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


async def test_fileresponse() -> None:
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
    assert "Content-Disposition" not in resp.headers

    download_resp = FileResponse(file_path, filename="zenofpython.txt")
    assert download_resp.headers["content-type"] == "application/octet-stream"
    assert (
        download_resp.headers["content-disposition"]
        == 'attachment; filename="zenofpython.txt"'
    )

    inline_resp = FileResponse(
        file_path,
        filename="zenofpython.txt",
        headers={"X-Test": "1"},
        content_disposition_type="inline",
    )
    assert (
        inline_resp.headers["content-disposition"]
        == 'inline; filename="zenofpython.txt"'
    )

    app1 = StreamingApp()
    await resp({}, app1.reiceive, app1.send)

    body_str = app1.body.decode("utf-8")
    assert "Beautiful is better than ugly." in body_str
    assert (
        "Namespaces are one honking great idea -- let's do more of those!" in body_str
    )

    custom_status_resp = FileResponse(file_path, status_code=404)
    assert custom_status_resp.status_code == 404
    assert custom_status_resp.headers["content-length"] == str(total_length)

    quoted_filename_resp = FileResponse(file_path, filename="zen of python.txt")
    assert (
        quoted_filename_resp.headers["content-disposition"]
        == "attachment; filename*=utf-8''zen%20of%20python.txt"
    )


def test_rangehandler() -> None:
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


def test_rangehandler_stops_on_empty_read() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")
    handler = RangeFileHandler(file_path)
    handler.set_range(0, 1)
    handler.file.seek(handler.file_size)

    with pytest.raises(StopIteration):
        next(handler)


def test_fileresponse_parse_request() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")

    handler = RangeFileHandler(file_path)

    req_headers = {
        "Range": "bytes=0-10",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)

    assert start == 0
    assert end == 11
    assert code == 206

    req_headers = {
        "Range": "bytes =-10",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)
    assert start == handler.file_size - 10
    assert end == handler.file_size
    assert code == 206

    req_headers = {
        "Range": "bytes=",
        "If-Range": handler.etag,
    }

    start, end, code = parse_request(handler, req_headers)
    assert start == 0
    assert end == handler.file_size
    assert code == 200

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


def test_fileresponse_parse_request_range_edges(tmp_path: t.Any) -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")
    handler = RangeFileHandler(file_path)

    start, end, code = parse_request(handler, {"Range": "items=0-1"})
    assert (start, end, code) == (0, handler.file_size, 200)

    start, end, code = parse_request(handler, {"Range": "bytes=5"})
    assert (start, end, code) == (0, handler.file_size, 200)

    start, end, code = parse_request(handler, {"Range": "bytes=-x"})
    assert (start, end, code) == (0, handler.file_size, 200)

    start, end, code = parse_request(handler, {"Range": "bytes=-0"})
    assert (start, end, code) == (0, handler.file_size, 416)

    start, end, code = parse_request(
        handler,
        {
            "Range": "bytes=0-1",
            "If-Range": handler.last_modified.replace(" UTC", ""),
        },
    )
    assert (start, end, code) == (0, 2, 206)

    empty_path = tmp_path / "empty.txt"
    empty_path.write_bytes(b"")
    empty_handler = RangeFileHandler(empty_path)
    start, end, code = parse_request(empty_handler, {"Range": "bytes=-1"})
    assert (start, end, code) == (0, 0, 416)


async def test_fileresponse_range_protocol() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")
    with open(file_path, "rb") as f:
        content = f.read()
    handler = RangeFileHandler(file_path)

    resp = FileResponse(file_path, headers={"Range": "bytes=0-9"})
    assert resp.status_code == 206
    assert resp.headers["content-range"] == f"bytes 0-9/{len(content)}"
    assert resp.headers["content-length"] == "10"

    app = StreamingApp()
    await resp({}, app.reiceive, app.send)
    assert app.status_code == 206
    assert app.body == content[:10]

    suffix_resp = FileResponse(file_path, headers={"Range": "bytes=-12"})
    app = StreamingApp()
    await suffix_resp({}, app.reiceive, app.send)
    assert suffix_resp.status_code == 206
    assert (
        suffix_resp.headers["content-range"]
        == f"bytes {len(content) - 12}-{len(content) - 1}/{len(content)}"
    )
    assert app.body == content[-12:]

    if_range_resp = FileResponse(
        file_path,
        headers={"Range": "bytes=0-9", "If-Range": handler.last_modified},
    )
    assert if_range_resp.status_code == 206

    stale_if_range_resp = FileResponse(
        file_path,
        headers={"Range": "bytes=0-9", "If-Range": "Wed, 21 Oct 2015 07:28:00 GMT"},
    )
    assert stale_if_range_resp.status_code == 200
    assert stale_if_range_resp.headers["content-length"] == str(len(content))

    unsatisfiable_resp = FileResponse(
        file_path, headers={"Range": f"bytes={len(content)}-"}
    )
    assert unsatisfiable_resp.status_code == 416
    assert unsatisfiable_resp.headers["content-range"] == f"bytes */{len(content)}"
    assert unsatisfiable_resp.headers["content-length"] == "0"


async def test_fileresponse_multiple_ranges() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")
    with open(file_path, "rb") as f:
        content = f.read()

    resp = FileResponse(file_path, headers={"Range": "bytes=0-4,10-14"})
    assert resp.status_code == 206
    assert resp.headers["content-type"].startswith("multipart/byteranges; boundary=")
    assert "content-range" not in resp.headers

    app = StreamingApp()
    await resp({}, app.reiceive, app.send)

    body = app.body
    assert b"Content-Range: bytes 0-4/" in body
    assert b"Content-Range: bytes 10-14/" in body
    assert content[:5] in body
    assert content[10:15] in body
    assert body.endswith(b"--unfazed-boundary--\r\n")


def test_multipart_range_handler_stops_when_file_ends() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "zenofpython.txt")
    file_size = os.stat(file_path).st_size
    handler = MultipartRangeFileHandler(
        file_path,
        [ByteRange(file_size - 1, file_size + 10)],
        boundary="unfazed-boundary",
        content_type="application/octet-stream",
        file_size=file_size,
    )

    body = b"".join(handler)
    assert body.endswith(b"--unfazed-boundary--\r\n")
