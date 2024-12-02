from datetime import timedelta
from enum import Enum, StrEnum

import pytest
from annotated_types import Ge, Le, MaxLen
from pydantic import Field
from tortoise import Model, fields

from tests.apps.serializer.models import Bag, Course, Student
from tests.apps.serializer.models import StudentProfile as Profile
from unfazed.serializer.tortoise import TSerializer, create_common_field


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
        exclude = ["is_active"]


class UserSerializer2(TSerializer):
    # override field
    height: int = Field(...)

    # extra field
    extra: str = Field(default="extra")

    class Meta:
        model = User


class UserSerializer3(TSerializer):
    class Meta:
        model = User
        include = ["height"]


def test_model_serializer_create() -> None:
    fields = UserSerializer.model_fields

    # test fields has beed created
    assert "id" in fields
    assert "bits" in fields
    # assert "is_active" in fields
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
        # is_active=True,
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

    # test valid data

    ins = UserSerializer3(height=1)
    assert ins.valid_data == {"height": 1}


def test_create_common_fields() -> None:
    pk = fields.BigIntField(primary_key=True, description="primary key")
    pk_type, pk_field = create_common_field(pk)

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

    _, f1_field = create_common_field(f1)

    assert f1_field.default == 1
    assert f1_field.is_required() is False

    _, f2_field = create_common_field(f2)
    assert f2_field.default_factory == gen_default
    assert f2_field.is_required() is False

    _, f3_field = create_common_field(f3)
    assert f3_field.is_required() is False

    _, f4_field = create_common_field(f4)
    assert f4_field.is_required() is True

    f5 = fields.DatetimeField(auto_now_add=True)
    f6 = fields.DatetimeField(auto_now=True)
    f7 = fields.DatetimeField()

    _, f5_field = create_common_field(f5)

    assert f5_field.default is None
    assert f5_field.is_required() is False

    _, f6_field = create_common_field(f6)
    assert f6_field.is_required() is False

    _, f7_field = create_common_field(f7)
    assert f7_field.is_required() is True

    # test enum field
    class Country(Enum):
        CN = 1
        USA = 2

    f8 = fields.IntEnumField(enum_type=Country, default=Country.CN)

    f8_type, f8_field = create_common_field(f8)
    assert f8_type == Country
    assert f8_field.default == Country.CN

    # test constraints
    f9 = fields.IntField()
    f10 = fields.BigIntField()
    f11 = fields.SmallIntField()
    f12 = fields.CharField(max_length=255)

    _, f9_field = create_common_field(f9)

    assert Ge(ge=-2147483648) in f9_field.metadata
    assert Le(le=2147483647) in f9_field.metadata

    _, f10_field = create_common_field(f10)
    assert Ge(ge=-9223372036854775808) in f10_field.metadata
    assert Le(le=9223372036854775807) in f10_field.metadata

    _, f11_field = create_common_field(f11)
    assert Ge(ge=-32768) in f11_field.metadata
    assert Le(le=32767) in f11_field.metadata

    _, f12_field = create_common_field(f12)
    assert MaxLen(max_length=255) in f12_field.metadata


def test_create_relational_fields() -> None:
    class StudentSerializer(TSerializer):
        class Meta:
            model = Student

    # db fields
    assert "id" in StudentSerializer.model_fields
    assert "name" in StudentSerializer.model_fields
    assert "age" in StudentSerializer.model_fields

    # m2m fields
    assert "courses" in StudentSerializer.model_fields

    # fk fields
    assert "bags" in StudentSerializer.model_fields
    print(StudentSerializer.model_fields)
    # one to one fields
    assert "profile" in StudentSerializer.model_fields

    # init model

    student = StudentSerializer(
        name="student1",
        age=18,
        courses=[
            {"name": "course1"},
            {"name": "course2"},
        ],
        bags=[
            {"name": "bag1"},
            {"name": "bag2"},
        ],
        profile={"nickname": "nick1"},
    )

    assert student.name == "student1"
    assert len(student.courses) == 2
    assert len(student.bags) == 2
    assert student.profile.nickname == "nick1"

    # relation fields default to None
    student = StudentSerializer(name="student1", age=18)

    assert student.name == "student1"
    assert student.courses is None
    assert student.bags is None
    assert student.profile is None

    # test profile serializer
    class ProfileSerializer(TSerializer):
        class Meta:
            model = Profile

    assert "id" in ProfileSerializer.model_fields
    assert "nickname" in ProfileSerializer.model_fields
    assert "student" in ProfileSerializer.model_fields
    assert "student_id" in ProfileSerializer.model_fields

    profile = ProfileSerializer(
        nickname="nick1", student={"name": "student1", "age": 18}, student_id=1
    )

    assert profile.nickname == "nick1"
    assert profile.student.name == "student1"
    assert profile.student.age == 18
    assert profile.student_id == 1

    # test bag serializer

    class BagSerializer(TSerializer):
        class Meta:
            model = Bag

    assert "id" in BagSerializer.model_fields
    assert "name" in BagSerializer.model_fields
    assert "student_id" in BagSerializer.model_fields

    bag = BagSerializer(
        name="bag1", student={"name": "student1", "age": 18}, student_id=1
    )
    assert bag.name == "bag1"
    assert bag.student.name == "student1"
    assert bag.student.age == 18
    assert bag.student_id == 1

    # test course serializer
    class CourseSerializer(TSerializer):
        class Meta:
            model = Course

    assert "id" in CourseSerializer.model_fields
    assert "name" in CourseSerializer.model_fields
    assert "students" in CourseSerializer.model_fields

    course = CourseSerializer(
        name="course1",
        students=[
            {"name": "student1", "age": 18},
            {"name": "student2", "age": 19},
        ],
    )

    assert course.name == "course1"
    assert len(course.students) == 2

    # test no model


def test_meta() -> None:
    with pytest.raises(ValueError):

        class NoModelSerializer(TSerializer):
            class Meta:
                foo = "bar"

    # test include exclude conflict
    with pytest.raises(ValueError):

        class IncludeExcludeConfict(TSerializer):
            class Meta:
                model = Student
                include = ["name"]
                exclude = ["name"]

    class IncludeSerializer(TSerializer):
        class Meta:
            model = Student
            include = ["name"]

    assert "name" in IncludeSerializer.Meta.include
    assert "age" in IncludeSerializer.Meta.exclude

    with pytest.raises(ValueError):

        class NoMetaSerializer(TSerializer):
            pass