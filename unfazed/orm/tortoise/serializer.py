import typing as t

import pydantic
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from tortoise.models import Model

from unfazed.serializer import BaseSerializer


class MetaClass(pydantic._internal._model_construction.ModelMetaclass):
    def __new__(
        mcs,
        name: str,
        bases: t.Tuple[t.Type],
        namespace: t.Dict[str, t.Any],
    ) -> t.Self:
        print("MetaClass", name, bases, namespace)
        cls = super().__new__(mcs, name, bases, namespace)
        thebase: "TSerializer" = None
        for base in bases:
            if base.__name__ == "TSerializer":
                thebase = base
                break

        if thebase is None:
            raise ValueError("BaseSerializer not found")

        if not hasattr(namespace, "Meta"):
            raise ValueError("Meta class not found")

        meta = namespace["Meta"]

        annotations = namespace.get("__annotations__", {})

        model: Model = meta.model

        # desc = model.describe(False)
        params: t.Dict[str, t.Tuple[t.Type, FieldInfo]] = {}
        for name, field in model._meta.fields_map.items():
            description = field.describe(False)
            field_info = FieldInfo(
                default=field.default,
                description=description["description"],
                title=description["title"],
            )

            params[name] = (name, field_info)

        for field in annotations:
            python_type = annotations[field]
            pydantic_field = None
            if field in namespace:
                pydantic_field = namespace[field]
            params[field] = (python_type, pydantic_field)

        cls.__doc__ = namespace.get("__doc__", meta.model.__doc__)

        return create_model(name, __base__=cls, __module__=cls.__module__, **params)


class TSerializer(BaseSerializer, metaclass=MetaClass):
    @property
    def valid_data(self) -> t.Dict[str, t.Any]:
        model: Model = self.Meta.model

        ret = []
        for name, field in model._meta.fields_map.items():
            if field.primary_key:
                continue
            ret.append(name)

    async def create(self, **kwargs: t.Any) -> t.Self:
        using_db = kwargs.pop("using_db", None)
        model: Model = self.Meta.model
        ins = await model.create(using_db=using_db, **kwargs)

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

    async def retrieve(self, instance: Model, **kwargs: t.Any) -> BaseModel:
        return self.model_validate(instance)

    async def destory(self, instance: Model, **kwargs: t.Any) -> None:
        using_db = kwargs.pop("using_db", None)
        await instance.delete(using_db=using_db)
