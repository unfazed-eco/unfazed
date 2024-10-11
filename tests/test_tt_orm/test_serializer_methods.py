import os
import typing as t
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from tests.apps.orm.serializer.models import Brand, Car, Color
from unfazed.core import Unfazed
from unfazed.orm.tortoise.commands import init_db, migrate
from unfazed.orm.tortoise.serializer import TSerializer


@pytest.fixture(scope="function")
async def prepare_db(tmp_path: Path, use_test_db: t.Generator) -> None:
    # init unfazed
    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.apps.orm.settings"
    unfazed = Unfazed()

    await unfazed.setup()

    # create migrations
    root_path = tmp_path / "serializer"
    root_path.mkdir()

    migrations_path = root_path / "migrations"

    cmd = init_db.Command(
        unfazed=unfazed, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"safe": True, "location": migrations_path})

    # migrate cmd
    cmd = migrate.Command(
        unfazed=unfazed, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path, "name": "add car model"})


class CarSerializer(TSerializer):
    override: int = 100
    cb_field: str = Field(default="cb")

    class Meta:
        model = Car


@pytest.mark.asyncio
async def test_serializer_methods(prepare_db: t.Generator) -> None:
    # create
    car = CarSerializer(
        bits=b"bits",
        limited=True,
        brand=Brand.BMW,
        alias="series 3",
        year="2023-11-14",
        release_datetime="2023-11-14 12:00:00",
        price=Decimal("100.00"),
        length=5.2,
        color=Color.RED,
        height=3,
        extra_info={"key": "value"},
        version=1,
        description="description",
        usage=timedelta(days=1),
        late_used_time="12:00:00",
        uuid=str(uuid.uuid4()),
    )

    assert "id" not in car.valid_data
    assert "production_datetime" not in car.valid_data

    new_ins = await car.create()

    assert new_ins.limited is True
    assert new_ins.brand == Brand.BMW

    # update

    car.alias = "series 5"
    car.version = 2
    car_ins = await Car.filter(id=new_ins.id).first()

    updated_ins = await car.update(car_ins)

    assert updated_ins.alias == "series 5"
    assert updated_ins.version == 2

    # destroy
    await car.destroy(car_ins)

    assert await Car.filter(id=updated_ins.id).count() == 0

    # from instance
    new_car = await Car.create(
        bits=b"bits",
        limited=True,
        brand=Brand.BMW,
        alias="series 3",
        year="2023-11-14",
        release_datetime="2023-11-14 12:00:00",
        price=Decimal("100.00"),
        length=5.2,
        color=Color.RED,
        height=3,
        extra_info={"key": "value"},
        version=1,
        description="description",
        usage=timedelta(days=1),
        late_used_time="12:00:00",
        uuid=str(uuid.uuid4()),
        override="1",
    )

    car = CarSerializer.from_instance(new_car)

    assert car.alias == "series 3"
    assert car.version == 1

    # get object
    class Ctx(BaseModel):
        id: int
        version: int

    ctx = Ctx(id=new_car.id, version=1)

    car = await CarSerializer.get_object(ctx)

    assert car.id == new_car.id
    assert car.version == new_car.version

    # get queryset
    queryset = await CarSerializer.get_queryset({"id": new_car.id})
    assert len(queryset) == 1

    # list
    for version in range(1, 10):
        await Car.create(
            bits=b"bits",
            limited=True,
            brand=Brand.BMW,
            alias="series 3",
            year="2023-11-14",
            release_datetime="2023-11-14 12:00:00",
            price=Decimal("100.00"),
            length=5.2,
            color=Color.RED,
            height=3,
            extra_info={"key": "value"},
            version=version,
            description="description",
            usage=timedelta(days=1),
            late_used_time="12:00:00",
            uuid=str(uuid.uuid4()),
            override="1",
        )

    ret = await CarSerializer.list(Car.filter(version__gt=5), page=1, size=2)

    assert ret.count == 4
    assert len(ret.data) == 2

    # list from ctx
    ret = await CarSerializer.list_from_ctx({"version__gt": 5}, page=1, size=2)
    assert ret.count == 4
    assert len(ret.data) == 2

    # list from queryset
    queryset = Car.filter(version__gt=5)
    ret = await CarSerializer.list_from_queryset(queryset, page=1, size=2)
    assert ret.count == 4
    assert len(ret.data) == 2

    class CarSchema(BaseModel):
        bits: bytes
        limited: bool
        brand: Brand
        alias: str
        year: str
        release_datetime: str
        price: Decimal
        length: float
        color: Color
        height: int
        extra_info: dict
        version: int
        description: str
        usage: timedelta
        late_used_time: str
        uuid: str
        override: int

    ctx = CarSchema(
        bits=b"bits",
        limited=True,
        brand=Brand.BMW,
        alias="series 3",
        year="2023-11-14",
        release_datetime="2023-11-14 12:00:00",
        price=Decimal("100.00"),
        length=5.2,
        color=Color.RED,
        height=3,
        extra_info={"key": "value"},
        version=100,
        description="description",
        usage=timedelta(days=1),
        late_used_time="12:00:00",
        uuid=str(uuid.uuid4()),
        override=1,
    )

    # create from ctx
    ret = await CarSerializer.create_from_ctx(ctx)
    assert ret.version == 100

    class UpdateCarSchema(BaseModel):
        id: int
        version: int

    ctx = UpdateCarSchema(id=new_car.id, version=101)
    # update from ctx
    ret = await CarSerializer.update_from_ctx(ctx)
    assert ret.version == 101

    # retrieve from ctx
    ctx = UpdateCarSchema(id=new_car.id, version=101)
    ret = await CarSerializer.retrieve_from_ctx(ctx)
    assert ret.version == 101

    # destroy from ctx
    ctx = UpdateCarSchema(id=new_car.id, version=101)
    await CarSerializer.destroy_from_ctx(ctx)
    assert await Car.filter(id=new_car.id).count() == 0
