import typing as t

from starlette.types import Scope as StarletteScope

from .base import Doc

Scope = t.Annotated[
    StarletteScope,
    Doc(
        description="ASGI Scope",
        example=StarletteScope,
    ),
]
