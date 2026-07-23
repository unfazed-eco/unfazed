from tortoise import Model, fields
from unfazed.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        table = "myapp_user"


class Student(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()

    class Meta:
        table = "student"


class Course(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    students = fields.ManyToManyField(
        "models.Student",
        related_name="courses",
        through="student_course",
        forward_key="course_id",
        backward_key="student_id",
    )

    class Meta:
        table = "course"


class StudentCourse(Model):
    id = fields.IntField(pk=True)
    student = fields.ForeignKeyField("models.Student", related_name="student_courses")
    course = fields.ForeignKeyField("models.Course", related_name="course_students")

    class Meta:
        table = "student_course"


class Book(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    owner = fields.ForeignKeyField("models.User", related_name="books")

    class Meta:
        table = "book"


class Profile(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    user = fields.OneToOneField("models.User", related_name="profile")

    class Meta:
        table = "profile"
