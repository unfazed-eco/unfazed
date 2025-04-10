import os
import typing as t

from .asgi import ASGIApp, Message, Receive, Scope, Send
from .base import Doc
from .cache import CacheBackend, CacheOptions
from .http import (
    ContentStream,
    GenericReponse,
    HttpMethod,
)

CanBeImported = t.Annotated[
    str,
    Doc(
        description="can be imported by unfazed.utils.import_string",
        example="unfazed.core.Unfazed",
    ),
]
Domain = t.Annotated[
    str,
    Doc(
        description="host:port",
        example="127.0.0.1:9527",
    ),
]

PathLike = t.Union[str, "os.PathLike[str]"]


__all__ = [
    "CanBeImported",
    "CacheOptions",
    "Domain",
    "HttpMethod",
    "GenericReponse",
    "ContentStream",
    "CacheBackend",
    "PathLike",
    "Scope",
    "ASGIApp",
    "Message",
    "Receive",
    "Send",
]
