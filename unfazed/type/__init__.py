import typing as t

from .base import Doc
from .cache import CacheOptions
from .http import GenericReponse, HttpMethod

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


__all__ = [
    "CanBeImported",
    "CacheOptions",
    "Domain",
    "HttpMethod",
    "GenericReponse",
]
