from datetime import timedelta
from enum import Enum, StrEnum

from annotated_types import Ge, Le, MaxLen
from pydantic import Field
from tortoise import fields

from unfazed.orm.tortoise import Model
from unfazed.orm.tortoise.serializer import TSerializer, field_creator


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"


class Country(Enum):
    CN = 1
    USA = 2


class User(Model):
    id = fields.BigIntField(primary_key=True)
    bits = fields.BinaryField()
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    sex = fields.CharEnumField(enum_type=Sex, max_length=255)
    year = fields.DateField()
    money = fields.DecimalField(max_digits=10, decimal_places=2)
    height = fields.FloatField()
    username = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    age = fields.IntField()
    country = fields.IntEnumField(enum_type=Country)
    description = fields.TextField()
    duration = fields.TimeDeltaField()
    time = fields.TimeField()
    uuid = fields.UUIDField()


class UserSerializer(TSerializer):
    class Meta:
        model = User


class UserSerializer2(TSerializer):
    # override field
    height: int = Field(...)

    # extra field
    extra: str = Field(default="extra")

    class Meta:
        model = User


def test_model_serializer_create() -> None:
    fields = UserSerializer.model_fields

    # test fields has beed created
    assert "id" in fields
    assert "bits" in fields
    assert "is_active" in fields
    assert "is_superuser" in fields
    assert "sex" in fields
    assert "year" in fields
    assert "money" in fields
    assert "height" in fields
    assert "username" in fields
    assert "created_at" in fields
    assert "updated_at" in fields
    assert "age" in fields
    assert "country" in fields
    assert "description" in fields
    assert "time" in fields
    assert "uuid" in fields
    assert "duration" in fields

    user = UserSerializer(
        id=1,
        bits=b"bits",
        is_active=True,
        is_superuser=True,
        sex=Sex.MALE,
        year="2021-01-01",
        money=100.0,
        height=1.75,
        username="max",
        age=18,
        country=Country.CN,
        description="description",
        time="12:00:00",
        uuid="123e4567-e89b-12d3-a456-426614174000",
        duration=timedelta(seconds=1),
    )

    assert user.id == 1

    fields = UserSerializer2.model_fields

    assert "height" in fields
    assert "extra" in fields

    user = UserSerializer2(
        id=1,
        bits=b"bits",
        is_active=True,
        is_superuser=True,
        sex=Sex.MALE,
        year="2021-01-01",
        money=100.0,
        height=11,
        username="max",
        age=18,
        country=Country.CN,
        description="description",
        time="12:00:00",
        uuid="123e4567-e89b-12d3-a456-426614174000",
        duration=timedelta(seconds=1),
    )

    assert user.height == 11
    assert user.extra == "extra"


def test_field_create() -> None:
    pk = fields.BigIntField(primary_key=True, description="primary key")
    pk_type, pk_field = field_creator(pk)

    # dont test title field dependently
    assert pk_type == int
    assert pk_field.description == "primary key"
    assert pk_field.default is None
    assert pk_field.is_required() is False

    # test default
    def gen_default():
        return 2

    f1 = fields.IntField(default=1)
    f2 = fields.IntField(default=gen_default)
    f3 = fields.IntField(null=True)
    f4 = fields.IntField()

    _, f1_field = field_creator(f1)

    assert f1_field.default == 1
    assert f1_field.is_required() is False

    _, f2_field = field_creator(f2)
    assert f2_field.default_factory == gen_default
    assert f2_field.is_required() is False

    _, f3_field = field_creator(f3)
    assert f3_field.is_required() is False

    _, f4_field = field_creator(f4)
    assert f4_field.is_required() is True

    f5 = fields.DatetimeField(auto_now_add=True)
    f6 = fields.DatetimeField(auto_now=True)
    f7 = fields.DatetimeField()

    _, f5_field = field_creator(f5)

    assert f5_field.default is None
    assert f5_field.is_required() is False

    _, f6_field = field_creator(f6)
    assert f6_field.is_required() is False

    _, f7_field = field_creator(f7)
    assert f7_field.is_required() is True

    # test enum field
    class Country(Enum):
        CN = 1
        USA = 2

    f8 = fields.IntEnumField(enum_type=Country, default=Country.CN)

    f8_type, f8_field = field_creator(f8)
    assert f8_type == Country
    assert f8_field.default == Country.CN

    # test constraints
    f9 = fields.IntField()
    f10 = fields.BigIntField()
    f11 = fields.SmallIntField()
    f12 = fields.CharField(max_length=255)

    _, f9_field = field_creator(f9)

    assert Ge(ge=-2147483648) in f9_field.metadata
    assert Le(le=2147483647) in f9_field.metadata

    _, f10_field = field_creator(f10)
    assert Ge(ge=-9223372036854775808) in f10_field.metadata
    assert Le(le=9223372036854775807) in f10_field.metadata

    _, f11_field = field_creator(f11)
    assert Ge(ge=-32768) in f11_field.metadata
    assert Le(le=32767) in f11_field.metadata

    _, f12_field = field_creator(f12)
    assert MaxLen(max_length=255) in f12_field.metadata


