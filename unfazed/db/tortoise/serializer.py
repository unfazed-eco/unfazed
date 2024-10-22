import typing as t
from datetime import time, timedelta

import pydantic
from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo
from tortoise.fields import TimeDeltaField, TimeField
from tortoise.fields.relational import (
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    ManyToManyRelation,
    OneToOneFieldInstance,
    ReverseRelation,
)
from tortoise.models import Field, Model
from tortoise.queryset import QuerySet

from unfazed.schema import Result
from unfazed.serializer import BaseSerializer


def create_m2m_field(field: ManyToManyFieldInstance) -> t.Tuple[t.Type, FieldInfo]:
    model: Model = field.related_model

    related_model_m2m_fields = model._meta.m2m_fields

    # exclude relation model when the model is already in the related model
    exclude: t.List[str] = list(model._meta.fetch_fields)

    for m2m_field in list(related_model_m2m_fields):
        if model._meta.fields_map[m2m_field].related_model == field.model:
            exclude.append(m2m_field)
            break

    pydantic_model = create_model_from_tortoise(
        model.__name__,
        model,
        exclude=exclude,
        module=model.__module__,
    )

    return t.Optional[t.List[pydantic_model]], FieldInfo(default=None)


def create_fk_field(field: ForeignKeyFieldInstance) -> t.Tuple[t.Type, FieldInfo]:
    model: Model = field.related_model

    exclude: t.List[str] = list(model._meta.fetch_fields) + [field.model_field_name]
    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)
    return t.Optional[pydantic_model], FieldInfo(default=None)


def create_bk_fk_field(field: BackwardFKRelation) -> t.Tuple[t.Type, FieldInfo]:
    model: Model = field.related_model

    related_model_fk_fields = model._meta.fk_fields
    exclude: t.List[str] = list(model._meta.fetch_fields)
    for fk_field in list(related_model_fk_fields):
        relation_model = model._meta.fields_map[fk_field]
        if relation_model.related_model == field.model:
            exclude.append(fk_field)
            exclude.append(relation_model.source_field)
            break

    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)

    return t.Optional[t.List[pydantic_model]], FieldInfo(default=None)


def create_o2o_field(field: OneToOneFieldInstance) -> t.Tuple[t.Type, FieldInfo]:
    model = field.related_model

    exclude: t.List[str] = list(model._meta.fetch_fields) + [field.model_field_name]
    pydantic_model = create_model_from_tortoise(
        model.__name__,
        model,
        exclude=exclude,
    )

    return t.Optional[pydantic_model], FieldInfo(default=None)


def create_bk_o2o_field(field: BackwardOneToOneRelation) -> t.Tuple[t.Type, FieldInfo]:
    model: Model = field.related_model

    related_model_o2o_fields = model._meta.o2o_fields

    exclude: t.List[str] = list(model._meta.fetch_fields)
    for o2o_field in list(related_model_o2o_fields):
        relation_model = model._meta.fields_map[o2o_field]
        if relation_model.related_model == field.model:
            exclude.append(o2o_field)
            exclude.append(relation_model.source_field)
            break

    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)

    return t.Optional[pydantic_model], FieldInfo(default=None)


def create_common_field(field: Field) -> t.Tuple[t.Type, FieldInfo]:
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

    # may be a bug for tortoise
    if description["field_type"] == TimeField:
        python_type = t.Union[time, timedelta]

    field_info = FieldInfo(
        default=default,
        default_factory=default_factory,
        description=description["description"] or "",
        title=description["name"] or "",
        **description["constraints"],
    )

    return python_type, field_info


def create_model_from_tortoise(
    cls_name: str,
    model: Model,
    *,
    namespace: t.Dict[str, t.Any] | None = None,
    base: t.Type | None = None,
    module: str | None = None,
    exclude: t.List[str] | None = None,
) -> BaseModel:
    namespace = namespace or {}
    annotations = namespace.get("__annotations__", {})
    params: t.Dict[str, t.Tuple[t.Type, FieldInfo]] = {}
    exclude = exclude or []

    relation_created_fields = []
    for name, field in model._meta.fields_map.items():
        if name in exclude:
            continue

        if name in model._meta.db_fields:
            params[name] = create_common_field(field)

        elif name in model._meta.m2m_fields:
            params[name] = create_m2m_field(field)

        elif name in model._meta.fk_fields:
            params[name] = create_fk_field(field)
            relation_created_fields.append(field.source_field)

        elif name in model._meta.backward_fk_fields:
            params[name] = create_bk_fk_field(field)

        elif name in model._meta.o2o_fields:
            params[name] = create_o2o_field(field)
            relation_created_fields.append(field.source_field)

        elif name in model._meta.backward_o2o_fields:
            params[name] = create_bk_o2o_field(field)

        else:
            raise ValueError(
                f"Tortoise bug: unknown field {name} in model {model.__qualname__}"
            )

    # delete fields created by relation
    for field_name in relation_created_fields:
        if field_name in params:
            del params[field_name]

    for field in annotations:
        python_type = annotations[field]
        pydantic_field = None
        if field in namespace:
            pydantic_field = namespace[field]
        params[field] = (python_type, pydantic_field)

    # handle config
    params["model_config"] = ConfigDict(from_attributes=True)

    return create_model(cls_name, __base__=base, __module__=module, **params)


def prepare_meta_config(cls_name: str, meta: t.Any) -> Model:
    if not hasattr(meta, "model"):
        raise ValueError(f"model not found in class {cls_name}")

    include = getattr(meta, "include", set())
    exclude = getattr(meta, "exclude", set())

    if include and exclude:
        raise ValueError(f"include and exclude cannot be used together for {cls_name}")

    model = meta.model
    if include:
        exclude = set(model._meta.fields_map.keys()) - set(include)

    else:
        include = set(model._meta.fields_map.keys()) - set(exclude)

    meta.include = include
    meta.exclude = exclude


class MetaClass(pydantic._internal._model_construction.ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: t.Tuple[t.Type],
        namespace: t.Dict[str, t.Any],
        *args,
        **kwargs,
    ) -> t.Type[BaseModel]:
        cls = super().__new__(mcs, cls_name, bases, namespace, *args, **kwargs)
        thebase: "TSerializer" = None
        for base in bases:
            if base.__name__ == "TSerializer":
                thebase = base
                break

        if thebase is None:
            return cls

        if "Meta" not in namespace:
            raise ValueError(f"Meta class not found for {cls_name}")

        meta = namespace["Meta"]

        prepare_meta_config(cls_name, meta)
        model: Model = meta.model

        cls.__doc__ = namespace.get("__doc__", meta.model.__doc__)

        # replaced by tortoise implementation
        return create_model_from_tortoise(
            cls_name,
            model,
            namespace=namespace,
            base=cls,
            module=cls.__module__,
            exclude=meta.exclude,
        )


class TSerializer(BaseSerializer, metaclass=MetaClass):
    # noinspection PyMethodParameters
    @pydantic.field_validator("*")  # It is a classmethod!
    def _tortoise_convert(cls, value: t.Any):  # pylint: disable=E0213
        # Computed fields
        if callable(value):
            return value()
        # Convert ManyToManyRelation to list
        if isinstance(value, (ManyToManyRelation, ReverseRelation)):
            return list(value)
        return value

    @property
    def valid_data(self) -> t.Dict[str, t.Any]:
        write_fields = self.get_write_fields()

        return {k: getattr(self, k) for k in write_fields}

    def get_write_fields(self) -> t.List[str]:
        ret = []

        fields_map: t.Dict[str, Field] = self.Meta.model._meta.fields_map
        db_fields: t.List[str] = self.Meta.model._meta.db_fields
        for name in db_fields:
            field = fields_map[name]
            # skip
            if field.pk or field.generated:
                continue

            if name not in self.Meta.include:
                continue

            if getattr(field, "auto_now", False) or getattr(
                field, "auto_now_add", False
            ):
                continue

            ret.append(name)

        return ret

    @classmethod
    def get_fetch_fields(cls) -> t.List[str]:
        return [
            ele for ele in cls.Meta.model._meta.fetch_fields if ele in cls.Meta.include
        ]

    @t.final
    async def create(self, **kwargs: t.Any) -> t.Self:
        using_db = kwargs.pop("using_db", None)
        model: Model = self.Meta.model
        ins = await model.create(using_db=using_db, **self.valid_data)

        return await self.retrieve(ins)

    @t.final
    async def update(self, instance: Model, **kwargs: t.Any) -> BaseModel:
        using_db = kwargs.pop("using_db", None)

        for k, v in self.model_dump(exclude_none=True).items():
            if k not in self.valid_data:
                continue
            if v is not None:
                setattr(instance, k, v)

        await instance.save(using_db=using_db)
        return await self.retrieve(instance)

    @t.final
    @classmethod
    async def retrieve(cls, instance: Model, **kwargs: t.Any) -> BaseModel:
        fetch_relations = kwargs.pop("fetch_relations", True)
        fetch_fields = cls.get_fetch_fields()
        if fetch_relations and fetch_fields:
            await instance.fetch_related(*fetch_fields)
        return cls.from_instance(instance)

    @t.final
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
        fetch_relations = kwargs.pop("fetch_relations", True)
        fetch_fields = cls.get_fetch_fields()
        if fetch_relations and fetch_fields:
            return model.filter(**cond).prefetch_related(*fetch_fields)
        return model.filter(**cond)

    @t.final
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
        # make sure set from_attributes=True
        return cls.model_validate(instance, from_attributes=True)
