import typing as t

from pydantic import BaseModel

if t.TYPE_CHECKING:
    from unfazed.http import HttpRequest  # pragma: no cover


class BaseAdmin(t.Protocol):
    if t.TYPE_CHECKING:
        name: str
        title: str

    async def has_view_perm(
        self, request: "HttpRequest", *args: t.Any, **kw: t.Any
    ) -> bool: ...
    async def has_change_perm(
        self, request: "HttpRequest", *args: t.Any, **kw: t.Any
    ) -> bool: ...
    async def has_delete_perm(
        self, request: "HttpRequest", *args: t.Any, **kw: t.Any
    ) -> bool: ...
    async def has_create_perm(
        self, request: "HttpRequest", *args: t.Any, **kw: t.Any
    ) -> bool: ...
    async def has_action_perm(
        self, request: "HttpRequest", *args: t.Any, **kw: t.Any
    ) -> bool: ...

    def get_actions(self) -> t.Dict[str, t.Any]: ...


class SerializedAdmin(t.Protocol):
    fields: t.Dict
    actions: t.Dict
    attrs: BaseModel

    def model_dump(self, *args: t.Any, **kw: t.Any) -> t.Dict[str, t.Any]: ...
