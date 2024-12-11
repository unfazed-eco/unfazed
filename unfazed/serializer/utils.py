import typing as t
from datetime import time, timedelta

from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo
from tortoise.fields import TimeDeltaField, TimeField
from tortoise.fields.relational import (
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    OneToOneFieldInstance,
)
from tortoise.models import Field, Model


def create_m2m_field(
    field: ManyToManyFieldInstance,
) -> t.Tuple[t.Any, FieldInfo]:
    model: t.Type[Model] = field.related_model

    related_model_m2m_fields = list(model._meta.m2m_fields)

    # exclude relation model when the model is already in the related model
    exclude: t.List[str] = list(model._meta.fetch_fields)

    for m2m_field in related_model_m2m_fields:
        m2m_model: ManyToManyFieldInstance = t.cast(
            ManyToManyFieldInstance, model._meta.fields_map[m2m_field]
        )
        if m2m_model.related_model == field.model:
            exclude.append(m2m_field)
            break

    # refer https://github.com/pydantic/pydantic/issues/5158
    pydantic_model = create_model_from_tortoise(
        model.__name__,
        model,
        exclude=exclude,
        module=model.__module__,
    )

    return t.Optional[t.List[pydantic_model]], FieldInfo(default=None)  # type: ignore


def create_fk_field(field: ForeignKeyFieldInstance) -> t.Tuple[t.Any, FieldInfo]:
    model: t.Type[Model] = field.related_model

    exclude: t.List[str] = list(model._meta.fetch_fields) + [field.model_field_name]
    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)
    return t.Optional[pydantic_model], FieldInfo(default=None)  # type: ignore


def create_bk_fk_field(
    field: BackwardFKRelation,
) -> t.Tuple[t.Any, FieldInfo]:
    model: t.Type[Model] = field.related_model

    related_model_fk_fields = model._meta.fk_fields
    exclude: t.List[str] = list(model._meta.fetch_fields)
    for fk_field in list(related_model_fk_fields):
        relation_model = t.cast(
            ForeignKeyFieldInstance, model._meta.fields_map[fk_field]
        )
        if relation_model.related_model == field.model:
            exclude.append(fk_field)
            if relation_model.source_field:
                exclude.append(relation_model.source_field)
            break

    # refer https://github.com/pydantic/pydantic/issues/5158
    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)

    return t.Optional[t.List[pydantic_model]], FieldInfo(default=None)  # type: ignore


def create_o2o_field(
    field: OneToOneFieldInstance,
) -> t.Tuple[t.Any, FieldInfo]:
    model = field.related_model

    exclude: t.List[str] = list(model._meta.fetch_fields) + [field.model_field_name]
    pydantic_model = create_model_from_tortoise(
        model.__name__,
        model,
        exclude=exclude,
    )

    return t.Optional[pydantic_model], FieldInfo(default=None)  # type: ignore


def create_bk_o2o_field(
    field: BackwardOneToOneRelation,
) -> t.Tuple[t.Any, FieldInfo]:
    model: t.Type[Model] = field.related_model

    related_model_o2o_fields = list(model._meta.o2o_fields)

    exclude: t.List[str] = list(model._meta.fetch_fields)
    for o2o_field in related_model_o2o_fields:
        relation_model = t.cast(
            OneToOneFieldInstance, model._meta.fields_map[o2o_field]
        )
        if relation_model.related_model == field.model:
            exclude.append(o2o_field)
            if relation_model.source_field:
                exclude.append(relation_model.source_field)
            break

    pydantic_model = create_model_from_tortoise(model.__name__, model, exclude=exclude)

    return t.Optional[pydantic_model], FieldInfo(default=None)  # type: ignore


def create_common_field(field: Field) -> t.Tuple[t.Any, FieldInfo]:
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

    # may be a bug in tortoise
    if description["field_type"] == TimeField:
        python_type = t.Union[time, timedelta]

    field_info = FieldInfo(
        default=default,
        default_factory=default_factory,
        description=description["description"] or "",
        title=description["name"] or "",
        json_schema_extra=field.describe(True),
        **description["constraints"],
    )

    return python_type, field_info


def create_model_from_tortoise(
    cls_name: str,
    model: t.Type[Model],
    *,
    namespace: t.Dict[str, t.Any] | None = None,
    base: t.Type | None = None,
    module: str | None = None,
    exclude: t.List[str] | None = None,
) -> t.Type[BaseModel]:
    namespace = namespace or {}
    annotations = namespace.get("__annotations__", {})
    params: t.Dict[str, t.Any] = {}
    exclude = exclude or []
    module = module or ""

    relation_created_fields = []

    for name, field in model._meta.fields_map.items():
        if name in exclude:
            continue

        if name in model._meta.db_fields:
            params[name] = create_common_field(field)

        elif name in model._meta.m2m_fields:
            params[name] = create_m2m_field(t.cast(ManyToManyFieldInstance, field))

        elif name in model._meta.fk_fields:
            params[name] = create_fk_field(t.cast(ForeignKeyFieldInstance, field))
            relation_created_fields.append(field.source_field)

        elif name in model._meta.backward_fk_fields:
            params[name] = create_bk_fk_field(t.cast(BackwardFKRelation, field))

        elif name in model._meta.o2o_fields:
            params[name] = create_o2o_field(t.cast(OneToOneFieldInstance, field))
            relation_created_fields.append(field.source_field)

        else:
            # backward_o2o_fields
            params[name] = create_bk_o2o_field(t.cast(BackwardOneToOneRelation, field))

    # delete fields created by relation
    # for field_name in relation_created_fields:
    #     if field_name in params:
    #         del params[field_name]

    for field in annotations:
        python_type = annotations[field]
        pydantic_field = None
        if field in namespace:
            pydantic_field = namespace[field]
        params[field] = (python_type, pydantic_field)

    # handle config
    params["model_config"] = ConfigDict(from_attributes=True)

    return create_model(cls_name, __base__=base, __module__=module, **params)


def prepare_meta_config(cls_name: str, meta: t.Any) -> None:
    if not hasattr(meta, "model"):
        raise ValueError(
            f"Unfazed.Serializer Error: model not found in class {cls_name}"
        )

    include: t.List = getattr(meta, "include", [])
    exclude: t.List = getattr(meta, "exclude", [])

    if include and exclude:
        raise ValueError(
            f"Unfazed.Serializer Error: include and exclude cannot be used together for {cls_name}"
        )

    model = meta.model
    if include:
        exclude = list(set(model._meta.fields_map.keys()) - set(include))

    else:
        include = list(set(model._meta.fields_map.keys()) - set(exclude))

    meta.include = list(include)
    meta.exclude = list(exclude)
