import os
import typing as t
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import Field

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
