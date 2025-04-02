import typing as t

from asgiref.typing import (
    ASGIApplication,
    ASGIReceiveCallable,
    ASGIReceiveEvent,
    ASGISendCallable,
    ASGISendEvent,
    HTTPScope,
)
from starlette.types import ASGIApp as StarletteASGIApp
from starlette.types import Message as StarletteMessage
from starlette.types import Receive as StarletteReceive
from starlette.types import Scope as StarletteScope
from starlette.types import Send as StarletteSend

from .base import Doc

Scope = t.Annotated[
    StarletteScope,
    Doc(
        description="ASGI Scope",
        example=HTTPScope,
    ),
]


Receive = t.Annotated[
    StarletteReceive,
    Doc(
        description="ASGI Receive",
        example=ASGIReceiveCallable,
    ),
]

Send = t.Annotated[
    StarletteSend,
    Doc(
        description="ASGI Send",
        example=ASGISendCallable,
    ),
]


Message = t.Annotated[
    StarletteMessage,
    Doc(
        description="ASGI Send/Receive Message",
        examples=[
            ASGIReceiveEvent,
            ASGISendEvent,
        ],
    ),
]


ASGIApp = t.Annotated[
    StarletteASGIApp,
    Doc(
        description="ASGI App",
        example=ASGIApplication,
    ),
]
