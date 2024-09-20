import typing as t
from enum import Enum, IntEnum
from functools import partial

from tortoise import fields as f
from tortoise.validators import Validator

if t.TYPE_CHECKING:
    from .models import Model


import orjson as json

CharEnumType = t.TypeVar("CharEnumType", bound=Enum)
IntEnumType = t.TypeVar("IntEnumType", bound=IntEnum)
JsonDumpsFunc = t.Callable[[t.Any], str]
JsonLoadsFunc = t.Callable[[t.Union[str, bytes]], t.Any]
JSON_DUMPS: JsonDumpsFunc = partial(json.dumps, separators=(",", ":"))
JSON_LOADS: JsonLoadsFunc = json.loads


class BigIntField(f.BigIntField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class BinaryField(f.BinaryField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class BooleanField(f.BooleanField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


@t.overload
def CharEnumField(
    enum_type: t.Type[CharEnumType],
    *,
    source_field: t.Optional[str] = None,
    generated: bool = False,
    primary_key: t.Optional[bool] = None,
    null: bool = False,
    default: t.Any = None,
    unique: bool = False,
    db_index: t.Optional[bool] = None,
    description: t.Optional[str] = None,
    model: t.Optional["Model"] = None,
    validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
    **kwargs: t.Any,
): ...


def CharEnumField(enum_type: t.Type[CharEnumType], *args, **kw):
    return f.CharEnumField(enum_type, *args, **kw)


class CharField(f.CharField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            max_length: int,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class DateField(f.DateField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class DatetimeField(f.DatetimeField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            auto_now: bool = False,
            auto_now_add: bool = False,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class DecimalField(f.DecimalField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            max_digits: int,
            decimal_places: int,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class FloatField(f.FloatField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


@t.overload
def IntEnumField(
    enum_type: t.Type[IntEnumType],
    source_field: t.Optional[str] = None,
    generated: bool = False,
    primary_key: t.Optional[bool] = None,
    null: bool = False,
    default: t.Any = None,
    unique: bool = False,
    db_index: t.Optional[bool] = None,
    description: t.Optional[str] = None,
    model: t.Optional["Model"] = None,
    validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
    **kwargs: t.Any,
): ...


def IntEnumField(enum_type: t.Type[IntEnumType], *args, **kw):
    return f.IntEnumField(enum_type, *args, **kw)


class IntField(f.IntField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            primary_key: t.Optional[bool] = None,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class JSONField(f.JSONField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            encoder: JsonDumpsFunc = JSON_DUMPS,
            decoder: JsonLoadsFunc = JSON_LOADS,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class SmallIntField(f.SmallIntField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            primary_key: t.Optional[bool] = None,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class TextField(f.TextField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            primary_key: t.Optional[bool] = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            null: bool = False,
            default: t.Any = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class TimeDeltaField(f.TimeDeltaField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class TimeField(f.TimeField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            auto_now: bool = False,
            auto_now_add: bool = False,
            *,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...


class UUIDField(f.UUIDField):
    if t.TYPE_CHECKING:

        @t.overload
        def __init__(
            self,
            source_field: t.Optional[str] = None,
            generated: bool = False,
            primary_key: t.Optional[bool] = None,
            null: bool = False,
            default: t.Any = None,
            unique: bool = False,
            db_index: t.Optional[bool] = None,
            description: t.Optional[str] = None,
            model: t.Optional["Model"] = None,
            validators: t.Optional[t.List[t.Union[Validator, t.Callable]]] = None,
            **kwargs: t.Any,
        ) -> None: ...
