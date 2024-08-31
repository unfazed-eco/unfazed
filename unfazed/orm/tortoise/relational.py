"""
set db_constraint to False by default
"""

import typing as t

from tortoise.fields.base import (
    CASCADE,
    OnDelete,
)
from tortoise.fields.relational import ForeignKeyField as _ForeignKeyField
from tortoise.fields.relational import ManyToManyField as _ManyToManyField
from tortoise.fields.relational import OneToOneField as _OneToOneField

from .models import Model

MODEL = t.TypeVar("MODEL", bound=Model)


def ForeignKeyField(
    model_name: str,
    related_name: t.Union[t.Optional[str], t.Literal[False]] = None,
    on_delete: OnDelete = CASCADE,
    db_constraint: bool = False,
    null: bool = False,
    **kwargs: t.Any,
):
    return _ForeignKeyField(
        model_name, related_name, on_delete, db_constraint, null, **kwargs
    )


def ManyToManyField(
    model_name: str,
    through: t.Optional[str] = None,
    forward_key: t.Optional[str] = None,
    backward_key: str = "",
    related_name: str = "",
    on_delete: OnDelete = CASCADE,
    db_constraint: bool = False,
    create_unique_index: bool = True,
    **kwargs: t.Any,
):
    return _ManyToManyField(
        model_name,
        through,
        forward_key,
        backward_key,
        related_name,
        on_delete,
        db_constraint,
        create_unique_index,
        **kwargs,
    )


def OneToOneField(
    model_name: str,
    related_name: t.Union[t.Optional[str], t.Literal[False]] = None,
    on_delete: OnDelete = CASCADE,
    db_constraint: bool = True,
    null: bool = False,
    **kwargs: t.Any,
):
    return _OneToOneField(
        model_name,
        related_name,
        on_delete,
        db_constraint,
        null,
        **kwargs,
    )
