import typing as t

from pydantic import BaseModel

from unfazed.protocol import BaseSerializer as BaseSerializerProtocol
from unfazed.protocol import QuerySet
from unfazed.schema import Result


class BaseSerializer(BaseModel, BaseSerializerProtocol):
    # used by endpoints directly

    @t.final
    @classmethod
    async def list_from_ctx(
        cls, cond: t.Dict, page: int, size: int, **kwargs
    ) -> Result:
        queryset = cls.get_queryset(cond, **kwargs)
        return await cls.list(queryset, page, size, **kwargs)

    @t.final
    @classmethod
    async def list_from_queryset(
        cls, queryset: QuerySet, page: int, size: int, **kwargs
    ) -> Result:
        return await cls.list(queryset, page, size, **kwargs)

    @t.final
    @classmethod
    async def create_from_ctx(cls, ctx: BaseModel, **kwargs) -> t.Self:
        serializer = cls(**ctx.model_dump(exclude_none=True))
        db_ins = await serializer.create(**kwargs)
        return await cls.retrieve(db_ins, **kwargs)

    @t.final
    @classmethod
    async def update_from_ctx(cls, ctx: BaseModel, **kwargs) -> t.Self:
        ins = await cls.get_object(ctx)
        serializer = cls.from_instance(ins)

        for field in ctx.model_fields:
            if hasattr(serializer, field):
                setattr(serializer, field, getattr(ctx, field))
        db_ins = await serializer.update(ins, **kwargs)
        return await cls.retrieve(db_ins, **kwargs)

    @t.final
    @classmethod
    async def destroy_from_ctx(cls, ctx: BaseModel, **kwargs) -> None:
        ins = await cls.get_object(ctx)
        return await cls.destroy(ins, **kwargs)

    @t.final
    @classmethod
    async def retrieve_from_ctx(cls, ctx: BaseModel, **kwargs) -> t.Self:
        ins = await cls.get_object(ctx)
        serializer = cls.from_instance(ins)
        return await serializer.retrieve(ins, **kwargs)
