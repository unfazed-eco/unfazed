from tortoise import Model, fields


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
    student = fields.ForeignKeyField("models.Student", related_name="courses")
    course = fields.ForeignKeyField("models.Course", related_name="students")

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
