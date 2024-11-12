import enum

from tortoise import fields as f
from tortoise.models import Model

from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.admin.registry import BaseModelAdmin, site
from unfazed.db.tortoise.serializer import TSerializer


def test_site() -> None:
    settings["UNFAZED_SETTINGS"] = UnfazedSettings(
        VERSION="0.1.0", PROJECT_NAME="Unfazed Admin"
    )
    route = site.to_route()

    assert route is None

    ret = site.to_serialize()
    assert ret.title == "Unfazed Admin"

    site.extra = {"foo": "bar"}
    ret = site.to_serialize()
    assert ret.extra == {"foo": "bar"}


def test_base_model_admin() -> None:
    class Brand(enum.StrEnum):
        BMW = "BMW"
        BENZ = "BENZ"

    class Color(enum.IntEnum):
        RED = 1
        GREEN = 2

    class Car(Model):
        id = f.BigIntField(primary_key=True)
        bits = f.BinaryField()
        limited = f.BooleanField()
        brand = f.CharEnumField(enum_type=Brand, default=Brand.BENZ)
        alias = f.CharField(max_length=100)
        year = f.DateField()
        production_datetime = f.DatetimeField(auto_now_add=True)
        release_datetime = f.DatetimeField()
        price = f.DecimalField(max_digits=10, decimal_places=2)
        length = f.FloatField()
        color = f.IntEnumField(enum_type=Color)
        height = f.IntField()
        extra_info = f.JSONField(default={})
        version = f.SmallIntField()
        description = f.TextField()
        usage = f.TimeDeltaField()
        late_used_time = f.TimeField()
        uuid = f.UUIDField()
        override = f.CharField(max_length=100)

        class Meta:
            table = "car"

    class CarSerializer(TSerializer):
        class Meta:
            model = Car

        extra: int

    class CarAdmin(BaseModelAdmin):
        serializer = CarSerializer

    instance = CarAdmin()

    fields = instance.get_fields()

    print(fields)

    raise NotImplementedError
