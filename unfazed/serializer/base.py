import typing as t

from pydantic import BaseModel

from unfazed.protocol import BaseSerializer as BaseSerializerProtocol
from unfazed.protocol import QuerySet
from unfazed.schema import Result


class BaseSerializer(BaseModel, BaseSerializerProtocol):
    # used by endpoints directly
    @classmethod
    async def list_from_ctx(
        cls, cond: t.Dict, page: int, size: int, **kwargs
    ) -> Result:
        queryset = await cls.get_queryset(cond, **kwargs)
        return await cls.list(queryset, page, size, **kwargs)

    @classmethod
    async def list_from_queryset(
        cls, queryset: QuerySet, page: int, size: int, **kwargs
    ) -> Result:
        return await cls.list(queryset, page, size, **kwargs)

    @classmethod
    async def create_from_ctx(cls, ctx: BaseModel, **kwargs) -> BaseModel:
        serializer = cls(**ctx.model_dump(exclude_none=True))
        return await serializer.create(**kwargs)

    @classmethod
    async def update_from_ctx(cls, ctx: BaseModel, **kwargs) -> BaseModel:
        ins = await cls.get_object(ctx)

        serializer = cls.model_validate(ins)
        return await serializer.update(ctx, **kwargs)

    @classmethod
    async def destroy_from_ctx(cls, ctx: BaseModel, **kwargs) -> None:
        ins = await cls.get_object(ctx)
        serializer = cls.from_orm(ins)
        await serializer.destroy(ins, **kwargs)

    @classmethod
    async def retrieve_from_ctx(cls, ctx: BaseModel, **kwargs) -> t.Self:
        ins = await cls.get_object(ctx)
        serializer = cls.from_orm(ins)
        return await serializer.retrieve(ins, **kwargs)
