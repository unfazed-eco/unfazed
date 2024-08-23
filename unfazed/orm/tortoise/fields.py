import typing as t

from tortoise.fields.relational import BackwardFKRelation as _BackwardFKRelation
from tortoise.fields.relational import (
    BackwardOneToOneRelation as _BackwardOneToOneRelation,
)
from tortoise.fields.relational import ForeignKeyField as _ForeignKeyField
from tortoise.fields.relational import (
    ForeignKeyNullableRelation as _ForeignKeyNullableRelation,
)
from tortoise.fields.relational import ForeignKeyRelation as _ForeignKeyRelation
from tortoise.fields.relational import ManyToManyField as _ManyToManyField
from tortoise.fields.relational import ManyToManyRelation as _ManyToManyRelation
from tortoise.fields.relational import OneToOneField as _OneToOneField
from tortoise.fields.relational import (
    OneToOneNullableRelation as _OneToOneNullableRelation,
)
from tortoise.fields.relational import OneToOneRelation as _OneToOneRelation
from tortoise.fields.relational import ReverseRelation as _ReverseRelation

from .models import Model

MODEL = t.TypeVar("MODEL", bound=Model)


class BackwardFKRelation(_BackwardFKRelation):
    def __init__(
        self,
        field_type: t.Type[MODEL],
        relation_field: str,
        relation_source_field: str,
        null: bool,
        description: t.Optional[str],
        **kwargs: t.Any,
    ) -> None:
        kwargs["db_constraint"] = False
        super().__init__(field_type, null=null, **kwargs)
        self.relation_field: str = relation_field
        self.relation_source_field: str = relation_source_field
        self.description: t.Optional[str] = description


class BackwardOneToOneRelation(_BackwardOneToOneRelation):
    def __init__(
        self,
        field_type: t.Type[MODEL],
        relation_field: str,
        relation_source_field: str,
        null: bool,
        description: t.Optional[str],
        **kwargs: t.Any,
    ) -> None:
        kwargs["db_constraint"] = False
        super().__init__(field_type, null=null, **kwargs)
        self.relation_field: str = relation_field
        self.relation_source_field: str = relation_source_field
        self.description: t.Optional[str] = description


class ForeignKeyField(_ForeignKeyField):
    pass


class ForeignKeyNullableRelation(_ForeignKeyNullableRelation):
    pass


class ForeignKeyRelation(_ForeignKeyRelation):
    pass


class ManyToManyField(_ManyToManyField):
    pass


class ManyToManyRelation(_ManyToManyRelation):
    pass


class OneToOneField(_OneToOneField):
    pass


class OneToOneNullableRelation(_OneToOneNullableRelation):
    pass


class OneToOneRelation(_OneToOneRelation):
    pass


class ReverseRelation(_ReverseRelation):
    pass
