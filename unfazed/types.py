import os
import typing as t

_ = t.Optional

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed

PathLike = t.Union[str, bytes, os.PathLike]
Context = t.Mapping[str, str | int | float]

type CanBeImported = t.Annotated[
    str,
    "split by dot, can be imported by importlib.import_module",
]
type Email = str
type TimeZone = str


type InstalledApp = t.Sequence[CanBeImported]
type Middlewares = t.Sequence[CanBeImported]


# TODO
# impl websockets protocol


class _Asgi(t.TypedDict):
    version: str
    spec_version: str


class _Scope(t.TypedDict):
    type: t.Annotated[str, "http"]
    asgi: _Asgi
    http_version: t.Annotated[
        str,
        "Version of the ASGI HTTP spec this server understands; one of '2.0', '2.1', '2.2' or '2.3'. Optional; if missing assume 2.0",
    ]
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: t.Sequence[t.Tuple[bytes, bytes]]
    client: t.Tuple[str, int]
    server: t.Tuple[str, int]
    state: dict | None
    app: "Unfazed"


type Scope = _Scope


class _BodyEvent(t.TypedDict):
    type: str
    body: bytes | None
    more_body: bool | None


type ReceiveEvent = _BodyEvent

type Receive = t.Callable[[], t.Awaitable[ReceiveEvent]]


class _StartSendEvent(t.TypedDict):
    type: str
    status: int
    headers: t.Sequence[t.Tuple[bytes, bytes]]
    trailers: bool | None


type SendEvent = _StartSendEvent | _BodyEvent


type Send = t.Callable[[SendEvent], t.Awaitable[None]]

type ASGIApp = t.Callable[[Scope, Receive, Send], t.Awaitable[None]]
