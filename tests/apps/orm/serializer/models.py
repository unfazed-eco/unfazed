import enum

from unfazed.orm.tortoise import Model
from unfazed.orm.tortoise import fields as f

"""
BigIntField,
BinaryField,
BooleanField,
CharEnumField,
CharField,
DateField,
DatetimeField,
DecimalField,
FloatField,
IntEnumField,
IntField,
JSONField,
SmallIntField,
TextField,
TimeDeltaField,
TimeField,
UUIDField,

"""


class Brand(enum.StrEnum):
    BMW = "BMW"
    BENZ = "BENZ"


class Color(enum.IntEnum):
    RED = 1
    GREEN = 2


class Car(Model):
    id = f.BigIntField(primary_key=True)
    bits = f.BinaryField(default=b"bits")
    limited = f.BooleanField()
    brand = f.CharEnumField(enum_type=Brand, default=Brand.BENZ)
    alias = f.CharField(max_length=100)
    year = f.DateField()
    production_datetime = f.DatetimeField(auto_now_add=True)
    release_datetime = f.DatetimeField()
    price = f.DecimalField(max_digits=10, decimal_place=2)
    length = f.FloatField()
    color = f.IntEnumField(enum_type=Color)
    height = f.IntField()
    extra_info = f.JSONField(default={})
    version = f.SmallIntField()
    description = f.TextField()
    usage = f.TimeDeltaField()
    late_used_time = f.TimeField()
    uuid = f.UUIDField()

    class Meta:
        table = "car"
