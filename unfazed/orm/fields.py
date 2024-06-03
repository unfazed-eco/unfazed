import typing as t

import sqlalchemy

# from pydantic.aliases import AliasChoices, AliasPath
from pydantic.fields import FieldInfo
from pydantic.types import Discriminator

type STE = sqlalchemy.types.TypeEngine


class ModelField[T](FieldInfo):
    def __init__(
        self,
        default: t.Any | None = None,
        *,
        default_factory: t.Callable[[], t.Any] | None = None,
        alias: str | None = None,
        alias_priority: int | None = None,
        # validation_alias: str | AliasPath | AliasChoices | None = None,
        serialization_alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        examples: list[t.Any] | None = None,
        exclude: bool | None = None,
        discriminator: str | Discriminator | None = None,
        frozen: bool | None = None,
        validate_default: bool | None = None,
        repr: bool | None = None,
        init: bool | None = None,
        init_var: bool | None = None,
        kw_only: bool | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        multiple_of: float | None = None,
        strict: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        db_column: str | None = None,
        db_comment: str | None = None,
        db_default: str | None = None,
        db_index: str | None = None,
        db_unique: bool | None = None,
        db_null: bool | None = None,
        primary_key: bool | None = None,
    ):
        super().__init__(
            default=default,
            default_factory=default_factory,
            alias=alias,
            alias_priority=alias_priority,
            # validation_alias=validation_alias,
            serialization_alias=serialization_alias,
            title=title,
            description=description,
            examples=examples,
            exclude=exclude,
            discriminator=discriminator,
            frozen=frozen,
            validate_default=validate_default,
            repr=repr,
            init=init,
            init_var=init_var,
            kw_only=kw_only,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            strict=strict,
            min_length=min_length,
            max_length=max_length,
        )

        self.db_column = db_column
        self.db_comment = db_comment or description
        self.db_default = db_default or self.get_default()
        self.db_index = db_index
        self.db_unique = db_unique
        self.db_null = db_null
        self.primary_key = primary_key

    def get_column(self, name: str) -> sqlalchemy.Column:
        return sqlalchemy.Column(
            name,
            self.get_column_type(),
            primary_key=self.primary_key,
            nullable=self.db_null,
            default=self.db_default,
            comment=self.db_comment,
            index=self.db_index,
            unique=self.db_unique,
        )

    def get_column_type(self) -> STE:
        raise NotImplementedError

    def to_python(self, value: T) -> T:
        return value

    def to_db(self, value: T) -> T:
        return value


class String(ModelField):
    def __init__(
        self,
        max_length: int,
        **kwargs,
    ):
        super().__init__(
            max_length=max_length,
            **kwargs,
        )

    def get_column_type(self) -> STE:
        return sqlalchemy.String(length=self.max_length)


class Text(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Text()


class JsonText(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Text()


class Integer(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Integer()


class BigInteger(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.BigInteger()


class SmallInteger(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.SmallInteger()


class DateTime(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.DateTime()


class Date(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Date()


class TsDateTime(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Integer()


class TsDate(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Integer()


class Time(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Time()


class Decimal(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.DECIMAL()


class Float(ModelField):
    def get_column_type(self) -> STE:
        return sqlalchemy.Float()
