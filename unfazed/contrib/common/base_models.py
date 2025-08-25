import time
import typing as t
from enum import IntEnum

import orjson as json
from tortoise import Model, fields
from tortoise.fields.relational import (
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    OneToOneFieldInstance,
)


class BaseModel(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.IntField(default=lambda: int(time.time()))
    updated_at = fields.IntField(default=lambda: int(time.time()))

    class Meta:
        abstract = True

    async def save(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.updated_at = int(time.time())
        await super().save(*args, **kwargs)


# TODO fix mypy error
# error: Metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
class JsonTextField(fields.TextField):  # type: ignore
    def to_db_value(self, value: t.Any, instance: t.Union[Model, t.Type[Model]]) -> str:
        try:
            return json.dumps(value).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to serialize value: {value}") from e

    def to_python_value(self, value: str) -> t.Any:
        if isinstance(value, (t.List, t.Dict)):
            return value
        try:
            return json.loads(value.encode())
        except Exception as e:  # pragma: no cover
            raise ValueError(
                f"Failed to deserialize value: {value}"
            ) from e  # pragma: no cover


class ActiveEnum(IntEnum):
    active = 1
    inactive = 0


def ForeignKeyField(
    model_name: str, related_name: str, null: bool = False, **kwargs: t.Any
) -> ForeignKeyFieldInstance:
    return ForeignKeyFieldInstance(
        model_name,
        related_name,
        db_constraint=False,
        on_delete=fields.NO_ACTION,
        null=null,
        **kwargs,
    )


def ManyToManyField(
    model_name: str,
    through: str,
    forward_key: str,
    backward_key: str,
    related_name: str,
    **kwargs: t.Any,
) -> ManyToManyFieldInstance:
    return ManyToManyFieldInstance(
        model_name,
        through,
        forward_key,
        backward_key,
        related_name,
        on_delete=fields.NO_ACTION,
        db_constraint=False,
        **kwargs,
    )


def OneToOneField(
    model_name: str, related_name: str, null: bool = False, **kwargs: t.Any
) -> OneToOneFieldInstance:
    return OneToOneFieldInstance(
        model_name,
        related_name,
        db_constraint=False,
        on_delete=fields.NO_ACTION,
        null=null,
        **kwargs,
    )
