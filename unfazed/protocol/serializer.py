import typing as t
from abc import ABC

from pydantic import BaseModel

from .orm import Model, QuerySet

if t.TYPE_CHECKING:
    from unfazed.schema import Relation, Result  # pragma: no cover


class BaseSerializer(ABC):
    class Meta:
        model: Model
        include: t.List[str] | None = None
        exclude: t.List[str] | None = None

    # implemented by orm driver
    @classmethod
    async def retrieve(cls, instance: Model, **kwargs: t.Any) -> t.Self: ...
    async def create(self, **kwargs: t.Any) -> Model: ...
    @classmethod
    async def destroy(self, instance: Model, **kwargs: t.Any) -> None: ...

    async def update(self, instance: Model, **kwargs: t.Any) -> Model: ...

    @classmethod
    async def list(
        cls, queryset: QuerySet, page: int, size: int, **kwargs
    ) -> "Result": ...

    @classmethod
    async def get_queryset(
        cls, cond: t.Dict[str, t.Any], **kwargs: t.Any
    ) -> QuerySet: ...

    @classmethod
    async def get_object(cls, ctx: BaseModel) -> Model: ...

    @classmethod
    async def from_instance(cls, instance: Model) -> t.Self: ...

    # implemented by base serializer
    @classmethod
    async def list_from_ctx(cls, ctx: BaseModel) -> "Result": ...

    @classmethod
    async def list_from_queryset(self, queryset: QuerySet) -> "Result": ...

    @classmethod
    async def create_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    async def update_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    async def destroy_from_ctx(cls, ctx: BaseModel) -> None: ...

    @classmethod
    async def retrieve_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    def find_relation(cls, other_cls: t.Type[t.Self]) -> t.Optional["Relation"]: ...
