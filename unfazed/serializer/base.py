import typing as t

import pydantic
from pydantic import BaseModel
from tortoise.fields.relational import (
    BackwardFKRelation,
    BackwardOneToOneRelation,
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    OneToOneFieldInstance,
)
from tortoise.models import Field, Model
from tortoise.queryset import QuerySet

from unfazed.schema import Relation, Result

from .utils import create_model_from_tortoise, prepare_meta_config


class QuerySetKwargs(t.TypedDict):
    order_by: t.NotRequired[t.Union[str, t.List[str], t.Tuple[str, ...]]]
    fetch_relations: t.NotRequired[bool]


class MetaClass(pydantic._internal._model_construction.ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: t.Tuple[t.Type],
        namespace: t.Dict[str, t.Any],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> t.Type[BaseModel]:
        cls = super().__new__(mcs, cls_name, bases, namespace, *args, **kwargs)
        thebase: t.Type["Serializer"] | None = None
        for base in bases:
            if base.__name__ == "Serializer":
                thebase = base
                break

        if thebase is None:
            return cls

        if "Meta" not in namespace:
            raise ValueError(
                f"Unfazed.Serializer Error: Meta class not found for {cls_name}"
            )

        meta = namespace["Meta"]

        prepare_meta_config(cls_name, meta)
        model: t.Type[Model] = meta.model

        cls.__doc__ = namespace.get("__doc__", meta.model.__doc__)

        # replaced by tortoise implementation
        return create_model_from_tortoise(
            cls_name,
            model,
            namespace=namespace,
            base=cls,
            module=cls.__module__,
            exclude=meta.exclude,
            enable_relations=meta.enable_relations,
        )


class Serializer(BaseModel, metaclass=MetaClass):
    """
    Serializer provides three functionalities:

    1. Generate a Serializer instance from a Tortoise Model
    2. Provide CRUD operations for Model instances
    3. Link with contrib.admin's ModelAdmin to support admin page


    Attention:

    the Serializer will automatically not only generate fields but also generate relation fields
    but due to the implementation of tortoise-orm, the relations between models are not directly accessible
    it must be accessed after `Tortoise.init` is called.

    refer: https://github.com/tortoise/tortoise-orm/blob/develop/examples/pydantic/early_init.py

    to avoid error when init Serializer, unfazed setup models immediately after collecting all apps.
    and devs need to know:

        1. avoid access Serializer in the app.ready() method.
        2. if you must access Serializer in the app.ready() method, override the realtions fields in the Serializer class.
            ```python

            class StudentSerializer(Serializer):
                class Meta:
                    model = Student

                courses: t.List[CourseSerializer] = []

            ```

        3. exclude the relation fields in the Meta.exclude

            ```python

            class StudentSerializer(Serializer):
                class Meta:
                    model = Student
                    exclude = ["courses"]


            ```


    Usage:


    ```python

    from tortoise import Model, fields
    from unfazed.serializer import Serializer

    class Student(Model):
        name = fields.CharField(max_length=255)
        age = fields.IntField()


    class StudentSerializer(Serializer):
        class Meta:
            model = Student

    # create a student

    class StudentCreate(BaseModel):
        name: str
        age: int

    StudentSerializer.list_from_ctx(StudentCreate(name="student1", age=18))

    # update a student

    class StudentUpdate(BaseModel):
        id: int
        name: str
        age: int

    StudentSerializer.update_from_ctx(StudentUpdate(id=1, name="student1", age=19))


    # delete a student

    class StudentDelete(BaseModel):
        id: int

    StudentSerializer.destroy_from_ctx(StudentDelete(id=1))

    # retrieve a student
    class StudentRetrieve(BaseModel):
        id: int

    StudentSerializer.retrieve_from_ctx(StudentRetrieve(id=1))


    # find relation


    class Course(Model):
        name = fields.CharField(max_length=255)
        students = fields.ManyToManyField("models.Student", related_name="courses")

    class CourseSerializer(Serializer):
        class Meta:
            model = Course

    StudentSerializer.find_relation(CourseSerializer)
    """

    class Meta:
        model: t.Type[Model]
        include: t.List[str] = []
        exclude: t.List[str] = []
        enable_relations: bool = False

    @t.final
    @classmethod
    async def list_from_ctx(
        cls,
        cond: t.Dict,
        page: int,
        size: int,
        **kwargs: t.Unpack[QuerySetKwargs],
    ) -> Result[t.Self]:
        queryset = cls.get_queryset(cond, **kwargs)
        return await cls.list(queryset, page, size)

    @t.final
    @classmethod
    async def list_from_queryset(
        cls,
        queryset: QuerySet,
        page: int,
        size: int,
        **kwargs: t.Unpack[QuerySetKwargs],
    ) -> Result[t.Self]:
        return await cls.list(queryset, page, size)

    @t.final
    @classmethod
    async def create_from_ctx(cls, ctx: BaseModel, **kwargs: t.Any) -> t.Self:
        serializer = cls(**ctx.model_dump(exclude_none=True))
        db_ins = await serializer.create(**kwargs)
        return await cls.retrieve(db_ins, **kwargs)

    @t.final
    @classmethod
    async def update_from_ctx(cls, ctx: BaseModel, **kwargs: t.Any) -> t.Self:
        ins = await cls.get_object(ctx)
        serializer = cls.from_instance(ins)

        for field in ctx.model_fields:
            if hasattr(serializer, field):
                setattr(serializer, field, getattr(ctx, field))
        db_ins = await serializer.update(ins, **kwargs)
        return await cls.retrieve(db_ins, **kwargs)

    @t.final
    @classmethod
    async def destroy_from_ctx(cls, ctx: BaseModel, **kwargs: t.Any) -> None:
        ins = await cls.get_object(ctx)
        return await cls.destroy(ins, **kwargs)

    @t.final
    @classmethod
    async def retrieve_from_ctx(cls, ctx: BaseModel, **kwargs: t.Any) -> t.Self:
        ins = await cls.get_object(ctx)
        serializer = cls.from_instance(ins)
        return await serializer.retrieve(ins, **kwargs)

    @property
    def valid_data(self) -> t.Dict[str, t.Any]:
        write_fields = self.get_write_fields()

        return {k: getattr(self, k) for k in write_fields}

    def get_write_fields(self) -> t.List[str]:
        ret = []

        fields_map: t.Dict[str, Field] = self.Meta.model._meta.fields_map
        db_fields: t.Set[str] = self.Meta.model._meta.db_fields
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
    async def create(self, **kwargs: t.Any) -> Model:
        using_db = kwargs.pop("using_db", None)
        model: t.Type[Model] = self.Meta.model
        ins = await model.create(using_db=using_db, **self.valid_data)

        return ins

    @t.final
    async def update(self, instance: Model, **kwargs: t.Any) -> Model:
        using_db = kwargs.pop("using_db", None)

        for k, v in self.model_dump(exclude_none=True).items():
            if k not in self.valid_data:
                continue
            if v is not None:
                setattr(instance, k, v)

        await instance.save(using_db=using_db)
        return instance

    @t.final
    @classmethod
    async def retrieve(cls, instance: Model, **kwargs: t.Any) -> t.Self:
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
        model: t.Type[Model] = cls.Meta.model
        if hasattr(ctx, "id"):
            return await model.get(id=ctx.id)
        else:
            raise ValueError("id not found")

    @classmethod
    def get_queryset(
        cls, cond: t.Dict[str, t.Any], **kwargs: t.Unpack[QuerySetKwargs]
    ) -> QuerySet:
        model: t.Type[Model] = cls.Meta.model
        fetch_relations = kwargs.pop("fetch_relations", True)
        fetch_fields = cls.get_fetch_fields()

        raw_query = model.filter(**cond)

        if "order_by" in kwargs:
            order_by_fields = []
            if isinstance(kwargs["order_by"], str):
                order_by_fields.append(kwargs["order_by"])
            elif isinstance(kwargs["order_by"], (t.List, t.Tuple)):  # type: ignore
                order_by_fields.extend(list(kwargs["order_by"]))
            else:
                raise ValueError("order_by must be a string or a list/tuple of strings")
            raw_query = raw_query.order_by(*order_by_fields)

        if fetch_relations and fetch_fields:
            return raw_query.prefetch_related(*fetch_fields)
        return raw_query

    @t.final
    @classmethod
    async def list(cls, queryset: QuerySet, page: int, size: int) -> Result[t.Self]:
        total = await queryset.count()

        if page == 0 or size <= 0:
            ins_list = await queryset.all()
        else:
            ins_list = await queryset.limit(size).offset((page - 1) * size)
        return Result(
            count=total,
            data=[cls.from_instance(ins) for ins in ins_list],
        )

    @classmethod
    def from_instance(cls, instance: Model) -> t.Self:
        mapping: t.Dict[str, t.Any] = {}
        for k, _ in instance._meta.fields_map.items():
            # skip relation fields
            temp = getattr(instance, k)
            if hasattr(temp, "_fetched") and temp._fetched is False:
                continue
            if isinstance(temp, QuerySet):
                continue
            mapping[k] = temp
        return cls.model_validate(mapping, from_attributes=True)

    @classmethod
    def find_relation(cls, other_cls: t.Type["Serializer"]) -> Relation | None:
        self_model: t.Type[Model] = cls.Meta.model
        other_model: t.Type[Model] = other_cls.Meta.model

        # check if it is a m2m relation
        for m2m_field_name in self_model._meta.m2m_fields:
            m2mfield: ManyToManyFieldInstance = t.cast(
                ManyToManyFieldInstance, self_model._meta.fields_map[m2m_field_name]
            )

            if m2mfield.related_model == other_model:
                # TODO: add through field
                return Relation(
                    target=other_cls.__name__,
                    source_field="",  # also field.related_name
                    target_field="",
                    relation="m2m",
                )

        # check if it is a fk relation
        for fk_field_name in self_model._meta.fk_fields:
            fk_field: ForeignKeyFieldInstance = t.cast(
                ForeignKeyFieldInstance, self_model._meta.fields_map[fk_field_name]
            )
            if fk_field.related_model == other_model:
                return Relation(
                    target=other_cls.__name__,
                    source_field=fk_field.source_field
                    or "",  # also fk_field.source_field
                    target_field=fk_field.to_field,
                    relation="fk",
                )

        # check if it is a bk_fk relation
        for bk_fk_field_name in self_model._meta.backward_fk_fields:
            bk_fk_field: BackwardFKRelation = t.cast(
                BackwardFKRelation, self_model._meta.fields_map[bk_fk_field_name]
            )
            if bk_fk_field.related_model == other_model:
                return Relation(
                    target=other_cls.__name__,
                    source_field="id",
                    target_field=bk_fk_field.relation_source_field,
                    relation="bk_fk",
                )

        # check if it is a o2o relation
        for o2o_field_name in self_model._meta.o2o_fields:
            o2o_field: OneToOneFieldInstance = t.cast(
                OneToOneFieldInstance, self_model._meta.fields_map[o2o_field_name]
            )
            if o2o_field.related_model == other_model:
                return Relation(
                    target=other_cls.__name__,
                    source_field=o2o_field.source_field or "",
                    target_field=o2o_field.to_field,
                    relation="o2o",
                )

        # check if it is a bk_o2o relation
        for bk_o2o_field_name in self_model._meta.backward_o2o_fields:
            bk_o2o_field: BackwardOneToOneRelation = t.cast(
                BackwardOneToOneRelation, self_model._meta.fields_map[bk_o2o_field_name]
            )
            if bk_o2o_field.related_model == other_model:
                return Relation(
                    target=other_cls.__name__,
                    source_field="id",
                    target_field=bk_o2o_field.relation_source_field,
                    relation="bk_o2o",
                )

        return None
