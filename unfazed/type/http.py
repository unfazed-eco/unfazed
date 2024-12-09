import typing as t

from pydantic import BaseModel

from .base import Doc

if t.TYPE_CHECKING:
    from unfazed.http import HttpResponse  # pragma: no cover

HttpMethod = t.Literal[
    "GET", "POST", "PATCH", "DELETE", "HEAD", "OPTIONS", "PUT", "TRACE"
]

GenericReponse = t.Annotated[
    t.Union[str, t.Dict[str, t.Any], BaseModel, "HttpResponse", t.List],
    Doc(
        description="""
        For gereric response, it can be a string, a dict or a pydantic model.

        Resp inherited by HttpResponse -> HttpResponse
        Dict -> JsonResponse
        BaseModel -> JsonResponse
        String -> HttpResponse

        """,
    ),
]


Content = t.Union[str, bytes, memoryview]
SyncContentStream = t.Iterable[Content]
AsyncContentStream = t.AsyncIterable[Content]
ContentStream = t.Union[AsyncContentStream, SyncContentStream]
