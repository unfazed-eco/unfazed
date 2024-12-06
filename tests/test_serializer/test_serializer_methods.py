import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import BaseModel, Field

from tests.apps.serializer.models import (
    Bag,
    Brand,
    Car,
    Color,
    Course,
    Student,
)
from tests.apps.serializer.models import StudentProfile as Profile
from unfazed.serializer import Serializer


class CarSerializer(Serializer):
    override: int = 100
    cb_field: str = Field(default="cb")

    class Meta:
        model = Car


async def test_serializer_methods() -> None:
    await Car.all().delete()
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
        id: int = -1
        version: int

    ctx = Ctx(id=new_car.id, version=1)

    car = await CarSerializer.get_object(ctx)

    assert car.id == new_car.id
    assert car.version == new_car.version

    # failed get object
    with pytest.raises(ValueError):

        class WrongCtx(BaseModel):
            version: int

        await CarSerializer.get_object(WrongCtx(version=1))

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

    ret2 = await CarSerializer.list(Car.filter(version__gt=5), page=0, size=0)
    assert ret2.count == 4
    assert len(ret2.data) == 4

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


async def test_relations() -> None:
    s1 = await Student.create(name="student1", age=18)
    s2 = await Student.create(name="student2", age=19)

    c1 = await Course.create(name="course1")
    await c1.students.add(s1)
    await c1.students.add(s2)
    c2 = await Course.create(name="course2")
    await c2.students.add(s2)

    await Bag.create(student=s1, name="bag1")
    await Bag.create(student=s1, name="bag2")
    await Bag.create(student=s2, name="bag3")

    await Profile.create(student=s1, nickname="profile1")

    class StudenSerializer(Serializer):
        class Meta:
            model = Student

    student = await Student.filter(id=s1.id).first()

    student_serializer = await StudenSerializer.retrieve(student)

    assert student_serializer.name == "student1"
    assert student_serializer.age == 18
    assert student_serializer.bags[0].name == "bag1"
    assert student_serializer.bags[1].name == "bag2"
    assert student_serializer.profile.nickname == "profile1"

    class CourseSerializer(Serializer):
        class Meta:
            model = Course

    course = await Course.filter(id=c1.id).first()

    course_serializer = await CourseSerializer.retrieve(course)

    assert course_serializer.name == "course1"
    assert course_serializer.students[0].name == "student1"
    assert course_serializer.students[1].name == "student2"

    class BagSerializer(Serializer):
        class Meta:
            model = Bag

    bag = await Bag.filter(student=s1).first()

    bag_serializer = await BagSerializer.retrieve(bag)

    assert bag_serializer.name == "bag1"
    assert bag_serializer.student.name == "student1"

    class ProfileSerializer(Serializer):
        class Meta:
            model = Profile

    profile = await Profile.filter(student=s1).first()

    profile_serializer = await ProfileSerializer.retrieve(profile)

    assert profile_serializer.student.name == "student1"
    assert profile_serializer.nickname == "profile1"

    # list_from_ctx

    ret = await StudenSerializer.list_from_ctx({"id": s1.id}, page=1, size=2)

    assert ret.count == 1
    assert len(ret.data) == 1

    assert ret.data[0].name == "student1"
    assert ret.data[0].age == 18
    assert ret.data[0].bags[0].name == "bag1"
    assert ret.data[0].bags[1].name == "bag2"
