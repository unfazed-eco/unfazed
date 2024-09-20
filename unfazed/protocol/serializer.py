import typing as t
from abc import ABC

from pydantic import BaseModel

from .orm import Model, QuerySet

if t.TYPE_CHECKING:
    from unfazed.schema import Result


class BaseSerializer(ABC):
    _model_creator: t.Callable[[t.Type[t.Self]], BaseModel]

    class Meta:
        model: Model
        include: t.List[str] | None = None
        exclude: t.List[str] | None = None

    @classmethod
    async def retrieve(cls, instance: Model, **kwargs: t.Any) -> BaseModel: ...
    async def create(self, **kwargs: t.Any) -> BaseModel: ...
    async def destroy(self, instance: Model, **kwargs: t.Any) -> None: ...
    async def update(self, instance: Model, **kwargs: t.Any) -> BaseModel: ...

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

    # used by endpoints directly
    @classmethod
    async def list_from_ctx(cls, ctx: BaseModel) -> "Result": ...

    @classmethod
    async def list_from_queryset(self, queryset: QuerySet) -> "Result": ...

    @classmethod
    async def create_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    async def update_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    async def destroy_from_ctx(cls, ctx: BaseModel) -> t.Self: ...

    @classmethod
    async def retrieve_from_ctx(cls, ctx: BaseModel) -> t.Self: ...
