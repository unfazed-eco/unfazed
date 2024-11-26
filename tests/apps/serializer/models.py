import enum

from tortoise import Model
from tortoise import fields as f


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
        table = "serializer_car"


# for test relationship
class Student(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)
    age = f.IntField()

    class Meta:
        table = "serializer_student"


class Bag(Model):
    id = f.BigIntField(primary_key=True)
    student = f.ForeignKeyField(
        "models.Student",
        related_name="bags",
        db_constraint=False,
        on_delete=f.NO_ACTION,
    )
    name = f.CharField(max_length=100)

    class Meta:
        table = "serializer_bag"


class StudentProfile(Model):
    id = f.BigIntField(primary_key=True)
    nickname = f.CharField(max_length=100)
    student = f.OneToOneField(
        "models.Student",
        related_name="profile",
        on_delete=f.NO_ACTION,
        db_constraint=False,
    )

    class Meta:
        table = "serializer_profile"


class Course(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)
    students = f.ManyToManyField(
        "models.Student",
        related_name="courses",
        on_delete=f.NO_ACTION,
        db_constraint=False,
    )

    class Meta:
        table = "serializer_course"


# class StudentCourseRelation(Model):
#     id = f.BigIntField(primary_key=True)
#     student = f.ForeignKeyField(
#         "models.Student",
#         related_name="course_relations",
#         db_constraint=False,
#         on_delete=f.NO_ACTION,
#     )
#     course = f.ForeignKeyField(
#         "models.Course",
#         related_name="student_relations",
#         db_constraint=False,
#         on_delete=f.NO_ACTION,
#     )

#     class Meta:
#         table = "student_course_relation"
