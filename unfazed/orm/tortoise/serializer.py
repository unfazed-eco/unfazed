import typing as t
from datetime import timedelta

import pydantic
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from tortoise.fields import TimeDeltaField
from tortoise.models import Field, Model
from tortoise.queryset import QuerySet

from unfazed.schema import Result
from unfazed.serializer import BaseSerializer

from . import utils as u


def field_creator(field: Field) -> t.Tuple[t.Type, FieldInfo]:
    description = field.describe(False)
    python_type = description["python_type"]
    # handle default
    default_factory = None
    if description["generated"]:
        default = None
    else:
        default = field.default
        if callable(default):
            default_factory = default
            default = ...
        elif default is None and (not field.null):
            default = ...  # required field

        if description.get("auto_now") or description.get("auto_now_add"):
            default = None  # handled by tortoise orm

    # handle enum
    if hasattr(field, "enum_type"):
        python_type = field.enum_type
        # clear constraints
        description["constraints"] = {}

    # handle timedelta
    if description["field_type"] == TimeDeltaField:
        python_type = timedelta

    field_info = FieldInfo(
        default=default,
        default_factory=default_factory,
        description=description["description"] or "",
        title=description["name"] or "",
        **description["constraints"],
    )

    return python_type, field_info


class MetaClass(pydantic._internal._model_construction.ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: t.Tuple[t.Type],
        namespace: t.Dict[str, t.Any],
        *args,
        **kwargs,
    ) -> t.Self:
        cls = super().__new__(mcs, cls_name, bases, namespace, *args, **kwargs)
        thebase: "TSerializer" = None
        for base in bases:
            if base.__name__ == "TSerializer":
                thebase = base
                break

        if thebase is None:
            return cls

        if "Meta" not in namespace:
            raise ValueError("Meta class not found")

        meta = namespace["Meta"]

        annotations = namespace.get("__annotations__", {})

        model: Model = meta.model

        params: t.Dict[str, t.Tuple[t.Type, FieldInfo]] = {}
        for name, field in model._meta.fields_map.items():
            params[name] = field_creator(field)

        for field in annotations:
            python_type = annotations[field]
            pydantic_field = None
            if field in namespace:
                pydantic_field = namespace[field]
            params[field] = (python_type, pydantic_field)

        cls.__doc__ = namespace.get("__doc__", meta.model.__doc__)

        return create_model(cls_name, __base__=cls, __module__=cls.__module__, **params)


class TSerializer(BaseSerializer, metaclass=MetaClass):
    @property
    def valid_data(self) -> t.Dict[str, t.Any]:
        write_fields = self.get_write_fields()

        return {k: getattr(self, k) for k in write_fields}

    def get_write_fields(self) -> t.List[str]:
        ret = []
        for name, field in self.Meta.model._meta.fields_map.items():
            # skip
            if field.pk or field.generated:
                continue

            if getattr(field, "auto_now", False) or getattr(
                field, "auto_now_add", False
            ):
                continue

            ret.append(name)

        return ret

    async def create(self, **kwargs: t.Any) -> t.Self:
        using_db = kwargs.pop("using_db", None)
        model: Model = self.Meta.model
        ins = await model.create(using_db=using_db, **self.valid_data)

        return await self.retrieve(ins)

    async def update(self, instance: Model, **kwargs: t.Any) -> BaseModel:
        using_db = kwargs.pop("using_db", None)

        for k, v in self.model_dump(exclude_none=True).items():
            if k not in self.valid_data:
                continue
            if v is not None:
                setattr(instance, k, v)

        await instance.save(using_db=using_db)
        return await self.retrieve(instance)

    @classmethod
    async def retrieve(cls, instance: Model, **kwargs: t.Any) -> BaseModel:
        return cls.from_instance(instance)

    @classmethod
    async def destroy(cls, instance: Model, **kwargs: t.Any) -> None:
        using_db = kwargs.pop("using_db", None)
        await instance.delete(using_db=using_db)

    @classmethod
    async def get_object(cls, ctx: BaseModel) -> Model:
        model: Model = cls.Meta.model
        if hasattr(ctx, "id"):
            return await model.get(id=ctx.id)
        else:
            raise ValueError("id not found")

    @classmethod
    def get_queryset(cls, cond: t.Dict[str, t.Any], **kwargs: t.Any) -> QuerySet:
        model: Model = cls.Meta.model
        return model.filter(**cond)

    @classmethod
    async def list(cls, queryset: QuerySet, page: int, size: int, **kwargs) -> Result:
        total = await queryset.count()

        if page == 0 or size <= 0:
            queryset = await queryset.all()
        else:
            queryset = await queryset.limit(size).offset((page - 1) * size)

        return Result(
            count=total,
            data=[cls.from_instance(ins) for ins in queryset],
        )

    @classmethod
    def from_instance(cls, instance: Model) -> BaseModel:
        return cls.model_validate(u.model_to_dict(instance))
